# Заголовки этапа 3
import yaml
from django.http import JsonResponse
from django.views import View
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests import get
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Заголовки этапа 4
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import *
from .serializers import *

@method_decorator(csrf_exempt, name='dispatch')
class PartnerUpdate(View):
    """
    Класс для обновления прайса от поставщика
    """

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        # Проверка типа пользователя (если реализовано поле user.type)
        # if getattr(request.user, 'type', '') != 'shop':
        #     return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                try:
                    response = get(url)
                    response.raise_for_status()
                    data = yaml.safe_load(response.content)
                except Exception as e:
                    return JsonResponse({'Status': False, 'Error': f'Ошибка загрузки файла: {str(e)}'})

                shop, _ = Shop.objects.get_or_create(name=data['shop'])  # Или используйте user_id

                # Обработка категорий
                for category_data in data.get('categories', []):
                    category_obj, _ = Category.objects.get_or_create(
                        id=category_data['id'],
                        defaults={'name': category_data['name']}
                    )
                    category_obj.shops.add(shop)

                # Очистка старых данных
                ProductInfo.objects.filter(shop=shop).delete()

                # Обработка товаров
                for item in data.get('goods', []):
                    product, _ = Product.objects.get_or_create(
                        name=item['name'],
                        category_id=item['category']
                    )

                    product_info = ProductInfo.objects.create(
                        external_id=item['id'],
                        product=product,
                        shop=shop,
                        name=item['name'],
                        price=item['price'],
                        price_rrc=item['price_rrc'],
                        quantity=item['quantity']
                    )

                    # Обработка параметров
                    for param_name, param_value in item.get('parameters', {}).items():
                        parameter_obj, _ = Parameter.objects.get_or_create(name=param_name)
                        ProductParameter.objects.create(
                            product_info=product_info,
                            parameter=parameter_obj,
                            value=param_value
                        )

                return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указан URL'})

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=400)

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
