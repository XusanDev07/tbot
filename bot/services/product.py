from django.shortcuts import get_object_or_404
from rest_framework import status
# from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, GenericAPIView
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bot.models import Product, Basket
from bot.serializers import ProductSerializer, BasketSerializer, BasketInProductSerializer


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
        return Product.objects.filter(new=True).select_related('ctg').all()

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
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()

        viewed_products = self.request.session.get('viewed_products', [])
        product_id = str(obj.id)

        if product_id not in viewed_products:
            viewed_products.append(product_id)
            if len(viewed_products) > 5:
                viewed_products.pop(0)

        self.request.session['viewed_products'] = viewed_products
        return obj


class LastViewedProductsView(APIView):
    def get(self, request):
        viewed_product_ids = request.session.get('viewed_products', [])
        viewed_products = Product.objects.filter(id__in=viewed_product_ids).select_related('ctg')
        serializer = ProductSerializer(viewed_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductFilterAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        name = self.request.query_params.get('name', '').lower()
        if not name:
            return list()
        return Product.objects.filter(name__icontains=name).select_related('ctg')
