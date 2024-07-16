from rest_framework import serializers

from .models import Product, Basket, Category


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
