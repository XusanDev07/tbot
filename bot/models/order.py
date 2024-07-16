from django.db import models

from bot.models import User
from bot.models.core import Product


class Order(models.Model):
    class PayStatus(models.IntegerChoices):
        Pending = 1, "Pending"  # yangi
        Shipped = 2, "Shipped"  # yetkazilmoqda
        Delivered = 3, "Delivered"  # yetkazilgan
        Cancelled = 4, "Cancelled"  # Bekor qilingan

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location_address = models.CharField(max_length=255)  # Example field for location address
    name = models.CharField(max_length=100)  # Example field for customer name
    comment = models.TextField(blank=True)  # Optional comment field
    total_amount_for_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price_of_products = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=PayStatus.choices, default=PayStatus.Pending)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.user.phone_number or self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.pk})"
