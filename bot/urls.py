from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bot.services import index
from bot.services.basket import BasketAPIView, BasketCreateAPIView, \
    BasketRetrieveUpdateAPIView, ABasket, DeleteUserBasketsAPIView, BasketCountAPIView
from bot.services.payment import CreateOrderAPIView, OrderListAPIView, OrderTypeAPIView, OrderStatusUpdateAPIView, \
    OrderDetailAPIView, OrderFilterUserAPIView, UserOrdersAPIView, PreOrderAPIView
from bot.services.product import ProductAPIView, ProductListAPIView, ProductDetailAPIView, LastViewedProductsView, \
    DiscountProductAPIView, ProductSimilarAPIView, ProductFilterAPIView, ProductNewAPIView
from bot.services.profile import ProfileAPIView
from bot.services.test import GetProOrderAPIView

urlpatterns = [
    path('product/', ProductAPIView.as_view()),
    path('product_new/', ProductNewAPIView.as_view()),
    path('all_product/', ProductListAPIView.as_view()),

    # path('ajal_api/', ProductInBasketAPIView.as_view()),

    path('product/<int:pk>/<int:tg_user_id>/', ProductDetailAPIView.as_view()),
    path('discount_product/', DiscountProductAPIView.as_view()),
    path('product_similar/<int:ctg_id>/', ProductSimilarAPIView.as_view()),
    path('l_v_product/<int:tg_user_id>/', LastViewedProductsView.as_view(), name='last_viewed_products'),
    path('search/product/<int:tg_user_id>/', ProductFilterAPIView.as_view(), name='search_product'),

    path('create_order/', CreateOrderAPIView.as_view(), name='create_order'),
    path('admin_order_list/', OrderListAPIView.as_view(), name='order_list'),
    path('order_type/', OrderTypeAPIView.as_view(), name='order_type'),
    path('orders/<int:order_id>/', OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
    path('order_detail/<int:pk>/', OrderDetailAPIView.as_view(), name='order-status-update'),
    path('order_user/<int:tg_user_id>/', OrderFilterUserAPIView.as_view(), name='order-status-update'),

    path('profile/<int:tg_user_id>/', ProfileAPIView.as_view(), name='profile'),

    path('get_basket/', BasketAPIView.as_view(), name='get_basket'),
    path('delete_basket/<int:tg_user_id>/', DeleteUserBasketsAPIView.as_view(), name='delete-user-baskets'),
    path('al/', ABasket.as_view(), name='get_basket'),
    path('_basket/<int:pk>/', BasketRetrieveUpdateAPIView.as_view(), name='update_basket'),
    # path('get_basket/<int:pk>/', BasketDetailAPIView.as_view(), name='get_basket_detail'),
    path('add_basket/', BasketCreateAPIView.as_view(), name='basket'),

]

urlpatterns += [
    path('order_item/<int:tg_user_id>/', UserOrdersAPIView.as_view(), name='user-orders'),
    path('pre_order/<int:tg_user_id>/', PreOrderAPIView.as_view(), name='user-pre-orders'),
    path('basket-count/<int:tg_user_id>/', BasketCountAPIView.as_view(), name='user-pre-orders'),
    path('test/<int:tg_user_id>/', GetProOrderAPIView.as_view(), name='user-pre-orders'),
]
