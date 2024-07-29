from django.db import models

from bot.models import User
from bot.models.core import Product


class Order(models.Model):
    class PayStatus(models.TextChoices):
        Yangi = "Yangi"
        Qabul_qilingan = "Qabul qilingan"
        Tayyor = "Tayyor"
        Yigilgan = "Yigilgan"
        Yetkazilmoqda = "Yetkazilmoqda"
        Yetkazilgan = "Yetkazilgan"
        Bekor_qilingan = "Bekor qilingan"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location_address = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    total_amount_for_payment = models.IntegerField(default=0)  # Amount in cents
    total_price_of_products = models.IntegerField(default=0)  # Amount in cents
    status = models.CharField(max_length=20, choices=PayStatus.choices, default=PayStatus.Yangi)
    delivery_type = models.BooleanField(default=True)  # True bo'lsa shaharga False bo'lsa qishloqga
    created_day = models.DateTimeField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)
    is_pre_order = models.BooleanField(default=False)  # Indicates if the order is a pre-order
    pre_order_availability_date = models.DateField(null=True,
                                                   blank=True)  # When the product is expected to be available

    def __str__(self):
        return f"Order #{self.user.phone_number or self.user.username} - {self.status} ({self.delivery_type})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.pk})"
