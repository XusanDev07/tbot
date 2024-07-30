from rest_framework import serializers
from rest_framework.generics import ListAPIView

from bot.models import Order, OrderItem
from bot.serializers import ProductSerializer


class OrderPreSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


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
