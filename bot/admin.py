from django.contrib import admin

from bot.models import User, Product, Basket, Category, Order, OrderItem, LastViewedProduct

admin.site.register(User)
admin.site.register(LastViewedProduct)
admin.site.register(Basket)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
