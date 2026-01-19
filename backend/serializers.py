from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')

    def create(self, validated_data):
        # Генерируем username из email
        user = User.objects.create_user(
            username=validated_data['email'],  # Используем email как username
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('user',)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


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
    product = serializers.StringRelatedField(source='product_info.product')
    price = serializers.IntegerField(source='product_info.price')
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity', 'total']

    def get_total(self, obj):
        return obj.product_info.price * obj.quantity

class OrderSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'dt', 'status', 'items']
