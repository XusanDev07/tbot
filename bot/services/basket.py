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


class BasketDetailAPIView(GenericAPIView):
    serializer_class = BasketSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('tg_user_id')
        if not user_id:
            return Basket.objects.none()
        return Basket.objects.filter(user__tg_user_id=user_id).select_related('product', 'product__ctg', 'user')

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user_id = self.request.query_params.get('tg_user_id')
        if not user_id:
            return Response({"detail": "tg_user_id is required"}, status=400)
        basket = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.get_serializer(basket)
        return Response(serializer.data)


class BasketRetrieveUpdateAPIView(GenericAPIView):
    serializer_class = UpdateBasketSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('tg_user_id')
        if not user_id:
            return Basket.objects.none()
        return Basket.objects.filter(user__tg_user_id=user_id).select_related('product', 'user')

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        basket = get_object_or_404(self.get_queryset(), id=pk)

        data = {
            "id": basket.id,
            "product": basket.product.name,
            "user": basket.user.username,
            "product_number": basket.product_number,
            "product_price": basket.product_price
        }
        return Response(data, status=status.HTTP_200_OK)

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
