from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from bot.models.auth import User


class Category(models.Model):
    name = models.CharField(max_length=999)


class Product(models.Model):
    name = models.CharField(max_length=500)
    img = models.ImageField(upload_to='product_img/')
    desc = models.CharField(max_length=5000, null=True)

    new = models.BooleanField(default=True)
    cost = models.IntegerField()  # FloatField()
    discount_price = models.IntegerField()  # FloatField()
    residual = models.SmallIntegerField()  # bu product qoldig'i

    ctg = models.ForeignKey(Category, models.SET_NULL, null=True, blank=True)

    sale = models.BooleanField(default=False)

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Basket(models.Model):
    product = models.ForeignKey(Product, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE, related_name='baskets', to_field='tg_user_id')
    product_number = models.IntegerField()
    product_price = models.IntegerField(editable=False)

    created = models.BooleanField(default=True)

    def format(self):
        return {
            "product_name": self.product.name,
            "username": self.user.username,
            "phone_number": self.user.phone_number,
        }

    def save(self, *args, **kwargs):
        if self.product_number > self.product.residual:
            raise ValidationError(f"Error: Only {self.product.residual} of {self.product.name} available in stock.")
        self.product_price = int(self.product_number * self.product.cost)
        super().save(*args, **kwargs)
