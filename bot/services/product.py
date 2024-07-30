from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
# from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, GenericAPIView
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bot.models import Product, Basket, User
from bot.models.core import LastViewedProduct
from bot.serializers import ProductSerializer, BasketSerializer, BasketInProductSerializer, LastProductSerializer, \
    BasketInProductFilterSerializer


class ProductAPIView(ListAPIView):
    serializer_class = BasketInProductSerializer

    def get_queryset(self):
        return Product.objects.select_related('ctg').all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductNewAPIView(ListAPIView):
    serializer_class = BasketInProductSerializer

    def get_queryset(self):
        return Product.objects.filter(new=True, sale=False).select_related('ctg').all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class DiscountProductAPIView(ListAPIView):
    serializer_class = BasketInProductSerializer

    def get_queryset(self):
        return Product.objects.filter(sale=True).select_related('ctg').all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.select_related('ctg')
    serializer_class = ProductSerializer


class ProductSimilarAPIView(GenericAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        ctg = self.kwargs.get('ctg_id')
        if ctg is None:
            return Product.objects.none()
        return Product.objects.filter(ctg_id=ctg).select_related('ctg')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailAPIView(RetrieveAPIView):
    queryset = Product.objects.select_related('ctg')
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        tg_user_id = kwargs.get('tg_user_id')

        if tg_user_id:
            try:
                user = User.objects.get(tg_user_id=tg_user_id)
                last_viewed_product, created = LastViewedProduct.objects.get_or_create(
                    product=product, user=user,
                    defaults={'viewed_at': timezone.now()}
                )
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LastViewedProductsView(ListAPIView):
    serializer_class = LastProductSerializer
    queryset = LastViewedProduct.objects.select_related('user', 'product')

    def get(self, request, *args, **kwargs):
        tg_user_id = kwargs.get('tg_user_id')
        last_viewed_products = LastViewedProduct.objects.filter(user__tg_user_id=tg_user_id)
        serializer = self.get_serializer(last_viewed_products, many=True)
        return Response(serializer.data)


class ProductFilterAPIView(ListAPIView):
    serializer_class = BasketInProductFilterSerializer

    def get_queryset(self):
        name = self.request.query_params.get('name', '').lower()

        if not name:
            return Product.objects.none()

        return Product.objects.filter(name__icontains=name).select_related('ctg')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'tg_user_id': self.kwargs.get('tg_user_id'),
        })
        return context
