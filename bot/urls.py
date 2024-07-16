from django.urls import path

from bot.services import index
from bot.services.basket import BasketAPIView, BasketCreateAPIView, BasketDetailAPIView, \
    BasketRetrieveUpdateAPIView
from bot.services.payment import CreateOrderAPIView
from bot.services.product import ProductAPIView, ProductListAPIView, ProductDetailAPIView, LastViewedProductsView, \
    DiscountProductAPIView, ProductSimilarAPIView, ProductFilterAPIView, ProductNewAPIView

urlpatterns = [
    # path('', index),
    path('product/', ProductAPIView.as_view()),
    path('product_new/', ProductNewAPIView.as_view()),
    path('all_product/', ProductListAPIView.as_view()),
    path('product/<int:pk>/', ProductDetailAPIView.as_view()),
    path('discount_product/', DiscountProductAPIView.as_view()),
    path('a/<int:ctg_id>/', ProductSimilarAPIView.as_view()),
    path('gg/', LastViewedProductsView.as_view(), name='last_viewed_products'),
    path('search/product/', ProductFilterAPIView.as_view(), name='search_product'),

    path('api/create_order/', CreateOrderAPIView.as_view(), name='create_order'),

    path('get_basket/', BasketAPIView.as_view(), name='get_basket'),

    path('api/update_basket/<int:pk>/', BasketRetrieveUpdateAPIView.as_view(), name='update_basket'),

    path('get_basket/<int:pk>/', BasketDetailAPIView.as_view(), name='get_basket_detail'),
    path('add_basket/', BasketCreateAPIView.as_view(), name='basket'),

]
