from django.db import models

from bot.models import User
from bot.models.core import Product


class Order(models.Model):
    class PayStatus(models.IntegerChoices):
        Pending = 1, "Pending"
        Shipped = 2, "Shipped"
        Delivered = 3, "Delivered"
        Cancelled = 4, "Cancelled"
        RegionDelivery = 5, "Delivery to Region"
        CityDelivery = 6, "Delivery to City"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location_address = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    total_amount_for_payment = models.IntegerField(default=0)  # Amount in cents
    total_price_of_products = models.IntegerField(default=0)  # Amount in cents
    status = models.CharField(max_length=20, choices=PayStatus.choices, default=PayStatus.Pending)
    delivery_type = models.CharField(max_length=20, choices=[
        ('region', 'Delivery to Region'),
        ('city', 'Delivery to City'),
    ], blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.user.phone_number or self.user.username} - {self.status}"

    def save(self, *args, **kwargs):
        # Convert delivery fees to cents
        if self.delivery_type == 'region':
            delivery_fee = 5000  # 50.00 USD in cents
        elif self.delivery_type == 'city':
            delivery_fee = 2000  # 20.00 USD in cents
        else:
            delivery_fee = 0

        # Ensure total_amount_for_payment is calculated using integers
        self.total_amount_for_payment = self.total_price_of_products + delivery_fee
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()  # Price in cents

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.pk})"
