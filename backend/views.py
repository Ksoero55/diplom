# Заголовки этапа 3
import yaml
from django.http import JsonResponse
from django.views import View
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests import get
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from django.contrib.auth.mixins import LoginRequiredMixin
# Заголовки этапа 4
from backend.services.partner_import import import_partner_data
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, BasePermission
# Заголовки email
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status

from django.contrib.auth import get_user_model

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        confirm_url = f"http://127.0.0.1:8000/api/confirm/{uid}/{token}/"

        send_mail(
            'Подтверждение регистрации',
            f'Перейдите по ссылке: {confirm_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

        return Response(
            {'detail': 'Письмо с подтверждением отправлено'},
            status=status.HTTP_201_CREATED
        )

class IsPartner(BasePermission):
    message = 'Доступ только для партнёров'

    def has_permission(self, request, view):
        return request.user.is_authenticated
        
class ConfirmEmailView(APIView):
    def get(self, request, uid, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({'detail': 'Неверная ссылка'}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'detail': 'Email подтверждён'})
        return Response({'detail': 'Ссылка недействительна'}, status=400)

class ContactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        contact = serializer.save(user=request.user)

        send_mail(
            subject='Адрес доставки сохранён',
            message='Вы успешно добавили адрес доставки.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
        )

        return Response({'Status': True, 'Data': serializer.data})

class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = request.data.get('url')

        if not url:
            return Response({'Status': False, 'Error': 'Не указан URL'}, status=400)

        try:
            import_partner_data(request.user, url)
        except Exception as e:
            return Response({'Status': False, 'Error': str(e)}, status=400)

        return Response({'Status': True})

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(username=email, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
            else:
                return Response({'error': 'Неверные учетные данные'}, status=400)
        return Response(serializer.errors, status=400)

class ProductsListAPIView(APIView):
    permission_classes = []

    def get(self, request):
        products = Product.objects.prefetch_related('product_infos', 'product_infos__parameters').all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = OrderItem.objects.filter(order__user=request.user, order__status='cart')
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id')
        shop_id = request.data.get('shop_id')
        quantity = int(request.data.get('quantity', 1))

        product_info = ProductInfo.objects.filter(product_id=product_id, shop_id=shop_id).first()
        if not product_info:
            return Response({'error': 'Товар не найден'}, status=400)

        order, created = Order.objects.get_or_create(user=request.user, status='cart')
        item, created = OrderItem.objects.get_or_create(
            order=order,
            product_info=product_info,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return Response({'message': 'Товар добавлен в корзину'})

    def delete(self, request):
        item_id = request.data.get('item_id')
        try:
            item = OrderItem.objects.get(id=item_id, order__user=request.user, order__status='cart')
            item.delete()
            return Response({'message': 'Товар удален из корзины'})
        except OrderItem.DoesNotExist:
            return Response({'error': 'Элемент не найден'}, status=400)

class ContactsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        contact_type = request.data.get('type', 'address')
        value = request.data.get('value')
        contact = Contact.objects.create(user=request.user, type=contact_type, value=value)
        return Response(ContactSerializer(contact).data, status=201)

    def delete(self, request):
        contact_id = request.data.get('id')
        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
            contact.delete()
            return Response({'message': 'Контакт удален'})
        except Contact.DoesNotExist:
            return Response({'error': 'Контакт не найден'}, status=400)

class ConfirmOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        contact_id = request.data.get('contact_id')
        try:
            order = Order.objects.get(user=request.user, status='cart')
            contact = Contact.objects.get(id=contact_id, user=request.user)
            order.contact = contact
            order.status = 'confirmed'
            order.save()
            return Response({'message': 'Заказ подтвержден'})
        except Order.DoesNotExist:
            return Response({'error': 'Корзина пуста'}, status=400)
        except Contact.DoesNotExist:
            return Response({'error': 'Контакт не найден'}, status=400)

class OrdersListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).exclude(status='cart')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
