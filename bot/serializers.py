from rest_framework import serializers

from .models import Product, Basket, Category, Order, User, LastViewedProduct


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    ctg = CategorySerializer(many=False)

    class Meta:
        model = Product
        fields = (
            'id', "name", "discount_percent", 'img', 'desc', 'new', 'cost', 'discount_price', 'residual', 'sale', 'ctg')


class LastProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = LastViewedProduct
        fields = ['id', 'product']


class BasketSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = Basket
        fields = "__all__"


class BasketInProductSerializer(serializers.ModelSerializer):
    basket_number = serializers.SerializerMethodField()
    ctg = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', "discount_percent", 'img', 'desc', 'new', 'cost', 'discount_price', 'residual', 'sale',
                  'ctg',
                  'basket_number']

    def get_basket_number(self, obj):
        tg_user_id = self.context.get('request').query_params.get('tg_user_id')

        print(f"Authenticated User ID: {tg_user_id}")  # Debugging line
        if tg_user_id is None:
            return 0

        basket = Basket.objects.filter(product=obj, user__tg_user_id=tg_user_id).first()
        print(f"Basket: {basket}")  # Debugging line

        if basket:
            return basket.product_number
        return 0


class BasketInProductFilterSerializer(serializers.ModelSerializer):
    basket_number = serializers.SerializerMethodField()
    ctg = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'discount_percent', 'img', 'desc', 'new', 'cost', 'discount_price', 'residual',
                  'sale', 'ctg', 'basket_number']

    def get_basket_number(self, obj):
        request = self.context.get('request')
        tg_user_id = self.context.get('tg_user_id')

        if tg_user_id is None:
            return 0

        basket = Basket.objects.filter(product=obj, user__tg_user_id=tg_user_id).first()

        if basket:
            return basket.product_number
        return 0


class BasketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = '__all__'

    def validate_product_number(self, value):
        if value < 0:
            raise serializers.ValidationError("Product number must be greater than or equal to 1.")
        return value


class UpdateBasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = ['product_number']

    def validate_product_number(self, value):
        if value < 0:
            raise serializers.ValidationError("Product number must be greater than or equal to 0.")
        return value


class CreateOrderSerializer(serializers.Serializer):
    tg_user_id = serializers.IntegerField()
    location_address = serializers.CharField(max_length=255)
    comment = serializers.CharField(allow_blank=True, required=False)
    delivery_type = serializers.BooleanField(default=True)
    total_price_of_products = serializers.IntegerField()


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
