from rest_framework import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView

from bot.models import Order, OrderItem
from bot.serializers import ProductSerializer


class OrderPreSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    created_day = serializers.SerializerMethodField()
    created_time = serializers.SerializerMethodField()
    total_price_of_products = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    delivery_type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price', 'order', 'created_day', 'created_time', 'total_price_of_products',
                  'location', 'delivery_type', 'status']

    def get_created_day(self, obj):
        if obj.order and obj.order.created_day:
            return obj.order.created_day.strftime("%B %d %Y")
        return None

    def get_created_time(self, obj):
        if obj.order and obj.order.created_time:
            return obj.order.created_time.strftime("%H:%M:%S")
        return None

    def get_total_price_of_products(self, obj):
        if obj.order and obj.order.total_price_of_products:
            return obj.order.total_price_of_products
        return None

    def get_location(self, obj):
        if obj.order and obj.order.location_address:
            return obj.order.location_address
        return None

    def get_status(self, obj):
        if obj.order and obj.order.status:
            return obj.order.status
        return None

    def get_delivery_type(self, obj):
        if obj.order and obj.order.delivery_type:
            return obj.order.delivery_type
        return None


class GetProOrderAPIView(ListAPIView):
    serializer_class = OrderPreSerializer

    def get_queryset(self):
        tg_user_id = self.kwargs.get('tg_user_id')
        orders = Order.objects.filter(user__tg_user_id=tg_user_id, is_pre_order=True)

        # Get the IDs of all the orders
        order_ids = orders.values_list('id', flat=True)

        # Filter OrderItem based on the order IDs
        order_items = OrderItem.objects.filter(order_id__in=order_ids).select_related('order', 'product',
                                                                                      'product__ctg')

        return order_items


class UserOrderStatusAPIView(ListAPIView):
    serializer_class = OrderPreSerializer

    def get_queryset(self):
        tg_user_id = self.kwargs.get('tg_user_id')
        status = self.request.query_params.get('status')
        if status and status.lower() == "hammasi":
            orders = Order.objects.filter(user__tg_user_id=tg_user_id)
        elif status:
            orders = Order.objects.filter(user__tg_user_id=tg_user_id, status__iexact=status.title())

        # Get the IDs of all the orders
        order_ids = orders.values_list('id', flat=True)

        # Filter OrderItem based on the order IDs
        order_items = OrderItem.objects.filter(order_id__in=order_ids).select_related('order', 'product',
                                                                                      'product__ctg')

        return order_items


class OrderDetailUserAPIView(ListAPIView):
    serializer_class = OrderPreSerializer
    lookup_field = 'order_id'

    def get_queryset(self):
        tg_user_id = self.kwargs.get('tg_user_id')
        order_id = self.kwargs.get('order_id')

        # Filter orders by user and order ID
        orders = Order.objects.filter(id=order_id, user__tg_user_id=tg_user_id)

        # Get order IDs for filtering order items
        order_ids = orders.values_list('id', flat=True)

        # Filter OrderItems based on the order IDs
        return OrderItem.objects.filter(order_id__in=order_ids).select_related('order', 'product', 'product__ctg')
