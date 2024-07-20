from rest_framework import serializers

from .models import Product, Basket, Category, Order, User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    ctg = CategorySerializer(many=False)

    class Meta:
        model = Product
        fields = ('id', "name", 'img', 'desc', 'new', 'cost', 'discount_price', 'residual', 'sale', 'ctg')


class BasketSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = Basket
        fields = "__all__"


class BasketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = '__all__'


class UpdateBasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = ['product_number']

    def validate_product_number(self, value):
        if value < 1:
            raise serializers.ValidationError("Product number must be greater than 0.")
        return value


class CreateOrderSerializer(serializers.Serializer):
    tg_user_id = serializers.CharField(max_length=255)
    location_address = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=100)
    comment = serializers.CharField(allow_blank=True, required=False)


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_status(self, obj):
        return obj.get_status_display()


class OrderTypeSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = '__all__'


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Order.PayStatus.choices)

    class Meta:
        model = Order
        fields = ['status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['status'] = instance.get_status_display()
        return representation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
