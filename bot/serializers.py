from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Product, Basket, Category, Order, User, LastViewedProduct, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    ctg = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)

    class Meta:
        model = Product
        fields = (
            'id', "name", "discount_percent", 'img', 'desc', 'new', 'cost', 'discount_price', 'residual', 'sale', 'ctg')

    def validate(self, data):
        """
        Check that discount_price is not greater than cost.
        """
        if 'cost' in data and 'discount_price' in data:
            if data['discount_price'] and data['discount_price'] > data['cost']:
                raise serializers.ValidationError("Discount price cannot be greater than cost.")
        return data

    def update(self, instance, validated_data):
        """
        Override update method to recalculate discount_percent.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.img = validated_data.get('img', instance.img)
        instance.desc = validated_data.get('desc', instance.desc)
        instance.new = validated_data.get('new', instance.new)
        instance.cost = validated_data.get('cost', instance.cost)
        instance.discount_price = validated_data.get('discount_price', instance.discount_price)
        instance.residual = validated_data.get('residual', instance.residual)
        instance.ctg = validated_data.get('ctg', instance.ctg)
        instance.sale = validated_data.get('sale', instance.sale)
        instance.save()
        return instance


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


class LastProductSerializer(serializers.ModelSerializer):
    product = BasketInProductSerializer(read_only=True)

    class Meta:
        model = LastViewedProduct
        fields = ['id', 'product']


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
    is_pre_order = serializers.BooleanField(default=False)
    pre_order_availability_date = serializers.DateField(required=False, allow_null=True)


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    user = serializers.CharField(source='user.username')

    created_day = serializers.SerializerMethodField()
    created_time = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_created_day(self, obj):
        return obj.created_day.strftime("%B %d %Y %H:%M:%S")

    def get_created_time(self, obj):
        return obj.created_time.strftime("%H:%M:%S.%f")

    def get_status(self, obj):
        return obj.get_status_display()


class OrderTypeSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = '__all__'


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.PayStatus.choices)

    def update(self, instance, validated_data):
        new_status = validated_data.get('status', instance.status)

        # Update the status of the order instance
        instance.status = new_status

        if new_status == Order.PayStatus.Yetkazilgan:
            self.update_product_quantities(instance)

        instance.save()
        return instance

    def update_product_quantities(self, order):
        for item in order.items.all():
            product = item.product
            if product.residual < item.quantity:
                raise ValidationError(
                    f"Error: Not enough stock for {product.name}. Available: {product.residual}, Requested: {item.quantity}")
            product.residual -= item.quantity
            product.save()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class ProductSerializera(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', "name", "discount_percent", 'img', 'desc', 'new', 'cost', 'discount_price', 'residual', 'sale', 'ctg')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializera()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderShowSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    created_day = serializers.SerializerMethodField()
    created_time = serializers.SerializerMethodField()
    total_price_of_products = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    delivery_type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['items', 'status', 'created_day', 'created_time', 'total_price_of_products', 'location',
                  'delivery_type']

    def get_created_day(self, obj):
        if obj.created_day:
            return obj.created_day.strftime("%B %d %Y")
        return None

    def get_created_time(self, obj):
        if obj.created_time:
            return obj.created_time.strftime("%H:%M:%S")
        return None

    def get_total_price_of_products(self, obj):
        if obj.total_price_of_products:
            return obj.total_price_of_products
        return None

    def get_location(self, obj):
        if obj.location_address:
            return obj.location_address
        return None

    def get_status(self, obj):
        if obj.status:
            return obj.status
        return None

    def get_delivery_type(self, obj):
        if obj.delivery_type:
            return obj.delivery_type
        return None
