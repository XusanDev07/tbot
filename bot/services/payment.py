from django.db import transaction
from django.shortcuts import get_object_or_404
from bot.models import Basket, Order, User, OrderItem
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from bot.serializers import CreateOrderSerializer


def create_order(user_id, location_address, name, comment):
    user = get_object_or_404(User, tg_user_id=user_id)
    baskets = Basket.objects.filter(user=user)

    if not baskets.exists():
        raise ValueError("No items in the basket for the specified user.")

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            location_address=location_address,
            name=name,
            comment=comment,
            total_amount_for_payment=0.00,
            total_price_of_products=0.00,
            status='Pending'
        )

        for basket in baskets:
            product = basket.product
            if basket.product_number > product.residual:
                raise ValueError(
                    f"Not enough residual for {product.name}. Available: {product.residual}, Requested: {basket.product_number}")

            product.residual -= basket.product_number
            product.save()

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=basket.product_number,
                price=basket.product_price
            )
            order.total_price_of_products += order_item.price

        order.total_amount_for_payment = order.total_price_of_products  # Example: Total amount includes product prices only
        order.save()

        baskets.delete()

    return order


class CreateOrderAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            tg_user_id = serializer.validated_data['tg_user_id']
            location_address = serializer.validated_data['location_address']
            name = serializer.validated_data['name']
            comment = serializer.validated_data.get('comment', '')

            try:
                order = create_order(tg_user_id, location_address, name, comment)
                return Response({"order_id": order.pk, "status": "Order created successfully."},
                                status=status.HTTP_201_CREATED)
            except ValueError as ve:
                return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
