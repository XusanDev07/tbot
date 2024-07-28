from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework import status as http_status, generics
from bot.models import Basket, Order, User, OrderItem
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from bot.serializers import CreateOrderSerializer, OrderSerializer, OrderStatusUpdateSerializer, OrderTypeSerializer


def create_order(user_id, location_address, comment, delivery_type):
    user = get_object_or_404(User, tg_user_id=user_id)
    baskets = Basket.objects.filter(user=user)

    if not baskets.exists():
        raise ValueError("No items in the basket for the specified user.")

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            location_address=location_address,
            delivery_type=delivery_type,
            comment=comment,
            total_amount_for_payment=0,  # Amount in cents
            total_price_of_products=0,  # Amount in cents
            status='Pending'
        )

        for basket in baskets:
            product = basket.product
            if basket.product_number > product.residual:
                raise ValueError(
                    f"Not enough residual for {product.name}. Available: {product.residual}, Requested: {basket.product_number}")

            product.residual -= basket.product_number
            product.save()

            # Calculate price in cents
            price_in_cents = int(basket.product_price * 100)
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=basket.product_number,
                price=price_in_cents
            )
            order.total_price_of_products += order_item.price

        # Save the order first to apply delivery fee logic
        order.save()

        # Calculate the total amount for payment after saving
        order.refresh_from_db()
        delivery_fee = 5000 if order.delivery_type == 'region' else 2000 if order.delivery_type == 'city' else 0
        order.total_amount_for_payment = order.total_price_of_products + delivery_fee
        order.save()

        baskets.delete()

    return order


class CreateOrderAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            tg_user_id = serializer.validated_data['tg_user_id']
            location_address = serializer.validated_data['location_address']
            delivery_type = serializer.validated_data['delivery_type']
            comment = serializer.validated_data.get('comment', '')

            try:
                order = create_order(tg_user_id, location_address, delivery_type, comment)
                return Response({"order_id": order.pk, "status": "Order created successfully."},
                                status=status.HTTP_201_CREATED)
            except ValueError as ve:
                return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListAPIView(ListAPIView):
    queryset = Order.objects.select_related('user')
    serializer_class = OrderSerializer


class OrderTypeAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        status = self.request.query_params.get('status')
        queryset = Order.objects.select_related('user')
        if status:
            queryset = queryset.filter(status__iexact=status)
        return queryset


class OrderStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs['pk'])
        serializer = self.get_serializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasketRetrieveUpdateAPIView(GenericAPIView):
    serializer_class = OrderStatusUpdateSerializer

    def get_queryset(self):
        return Order.objects.all()

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        basket = get_object_or_404(self.get_queryset(), id=pk)

        serializer = self.get_serializer(basket, data=request.data)
        if serializer.is_valid():
            new_product_number = serializer.validated_data['product_number']
            product = basket.product

            if new_product_number > product.residual + basket.product_number:
                return Response(
                    {
                        "error": f"Error: Only {product.residual + basket.product_number} of {product.name} available in residual."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            residual_difference = new_product_number - basket.product_number
            basket.product_number = new_product_number
            basket.product_price = int(new_product_number * product.cost)

            basket.save()
            return Response({"status": "Basket updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
