from django.contrib import admin
from .models import (
    Shop, Category, Product, ProductInfo,
    Parameter, ProductParameter, Order, OrderItem, Contact
)

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'url']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['shops']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ['product', 'shop', 'name', 'quantity', 'price']

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ['product_info', 'parameter', 'value']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'dt', 'status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'shop', 'quantity']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['type', 'user', 'value']
