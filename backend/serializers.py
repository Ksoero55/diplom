from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'type', 'value']

class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ['name', 'shop', 'quantity', 'price']

class ProductParameterSerializer(serializers.ModelSerializer):
    parameter_name = serializers.ReadOnlyField(source='parameter.name')
    class Meta:
        model = ProductParameter
        fields = ['parameter_name', 'value']

class ProductSerializer(serializers.ModelSerializer):
    product_infos = ProductInfoSerializer(many=True, read_only=True)
    parameters = ProductParameterSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'product_infos', 'parameters']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    shop_name = serializers.ReadOnlyField(source='shop.name')
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.quantity * obj.product_info.price

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'shop_name', 'quantity', 'product_info__price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'dt', 'status', 'items']
