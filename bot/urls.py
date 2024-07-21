from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bot.services import index
from bot.services.basket import BasketAPIView, BasketCreateAPIView, \
    BasketRetrieveUpdateAPIView, ABasket
from bot.services.payment import CreateOrderAPIView, OrderListAPIView, OrderTypeAPIView, OrderStatusUpdateAPIView
from bot.services.product import ProductAPIView, ProductListAPIView, ProductDetailAPIView, LastViewedProductsView, \
    DiscountProductAPIView, ProductSimilarAPIView, ProductFilterAPIView, ProductNewAPIView
from bot.services.profile import ProfileAPIView

urlpatterns = [
    path('product/', ProductAPIView.as_view()),
    path('product_new/', ProductNewAPIView.as_view()),
    path('all_product/', ProductListAPIView.as_view()),

    # path('ajal_api/', ProductInBasketAPIView.as_view()),

    path('product/<int:pk>/', ProductDetailAPIView.as_view()),
    path('discount_product/', DiscountProductAPIView.as_view()),
    path('product_similar/<int:ctg_id>/', ProductSimilarAPIView.as_view()),
    path('l_v_product/', LastViewedProductsView.as_view(), name='last_viewed_products'),
    # path('bbbbb/', add_basket, name='last_viewed_products'),
    path('search/product/', ProductFilterAPIView.as_view(), name='search_product'),

    path('api/create_order/', CreateOrderAPIView.as_view(), name='create_order'),
    path('admin_order_list/', OrderListAPIView.as_view(), name='order_list'),
    path('order_type/', OrderTypeAPIView.as_view(), name='order_type'),
    path('update_order_status/<int:pk>/', OrderStatusUpdateAPIView.as_view(), name='update-order-status'),

    path('profile/<int:tg_user_id>/', ProfileAPIView.as_view(), name='profile'),

    path('get_basket/', BasketAPIView.as_view(), name='get_basket'),
    path('al/', ABasket.as_view(), name='get_basket'),
    path('_basket/<int:pk>/', BasketRetrieveUpdateAPIView.as_view(), name='update_basket'),
    # path('get_basket/<int:pk>/', BasketDetailAPIView.as_view(), name='get_basket_detail'),
    path('add_basket/', BasketCreateAPIView.as_view(), name='basket'),

]
