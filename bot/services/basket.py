from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView

from bot.models import Basket, Product, User
from bot.serializers import BasketSerializer, BasketCreateSerializer, UpdateBasketSerializer


class BasketCreateAPIView(CreateAPIView):
    queryset = Basket.objects.all()
    serializer_class = BasketCreateSerializer

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        tg_user_id = self.request.data.get('user')
        product_number = int(self.request.data.get('product_number', 0))

        if not product_id or not tg_user_id:
            raise ValueError("You need to provide product_id and tg_user_id")

        product = Product.objects.get(id=product_id)
        user = User.objects.get(tg_user_id=tg_user_id)

        # Use filter instead of get to handle multiple entries
        baskets = Basket.objects.filter(product=product, user=user)

        if baskets.exists():
            basket = baskets.first()
            if int(product_number) == 0:
                basket.delete()
            else:
                basket.product_number = product_number
                basket.save()
        else:
            basket = Basket.objects.create(
                product=product,
                user=user,
                product_number=product_number
            )

        return basket

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        basket = self.perform_create(serializer)
        return Response(self.get_serializer(basket).data, status=status.HTTP_201_CREATED)


class BasketAPIView(GenericAPIView):
    serializer_class = BasketSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('tg_user_id')
        if not user_id:
            return Basket.objects.none()
        return Basket.objects.filter(user__tg_user_id=user_id).select_related('product', 'product__ctg', 'user')

    # 🤯 😱 vashe chuntirib bo'medi'

    def get(self, request, *args, **kwargs):
        basket = self.get_queryset()
        serializer = self.get_serializer(basket, many=True)
        return Response(serializer.data)


class ABasket(APIView):
    def post(self, request):
        data = request.data
        tg_user_id = request.query_params.get('tg_user_id')

        product_ids = data.get('product_ids', [])
        existing_cart = Basket.objects.filter(user__tg_user_id=tg_user_id).first()

        if existing_cart:
            cart = existing_cart
        else:
            user = get_object_or_404(User, tg_user_id=tg_user_id)
            cart = Basket.objects.create(user=user)
            cart.save()  # Ensure the Basket is saved and has an ID

        for product_id in product_ids:
            product = get_object_or_404(Product, id=product_id)
            cart.product.add(product)

        cart.save()  # Save any changes made to the Basket
        return Response({"cart_id": cart.id}, status=status.HTTP_201_CREATED)


class BasketRetrieveUpdateAPIView(GenericAPIView):
    serializer_class = UpdateBasketSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('tg_user_id')
        if not user_id:
            return Basket.objects.none()
        return Basket.objects.filter(user__tg_user_id=user_id).select_related('product', 'user', 'product__ctg')

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        basket = get_object_or_404(self.get_queryset(), id=pk)
        serializer = BasketSerializer(basket)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        basket = get_object_or_404(self.get_queryset(), id=pk)

        serializer = self.get_serializer(basket, data=request.data, partial=True)
        if serializer.is_valid():
            new_product_number = serializer.validated_data['product_number']

            if new_product_number == 0:
                basket.delete()
                return Response({"status": "Basket deleted successfully."}, status=status.HTTP_200_OK)

            product = basket.product

            if new_product_number > product.residual + basket.product_number:
                return Response(
                    {
                        "error": f"Error: Only {product.residual + basket.product_number} of {product.name} available in residual."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            residual_difference = new_product_number - basket.product_number
            basket.product_number = new_product_number
            basket.product_price = int(new_product_number * product.cost)

            basket.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
