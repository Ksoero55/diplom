import yaml
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db import transaction
from requests import get

from backend.models import (
    Shop, Category, Product, ProductInfo, Parameter, ProductParameter
)


@transaction.atomic
def import_partner_data(user, url):
    """
    Импорт прайса партнёра по URL (YAML)
    """

    validate_url = URLValidator()
    validate_url(url)

    response = get(url)
    response.raise_for_status()
    data = yaml.safe_load(response.content)

    shop, _ = Shop.objects.get_or_create(
        name=data['shop']
    )

    # Категории
    for category_data in data.get('categories', []):
        category_obj, _ = Category.objects.get_or_create(
            id=category_data['id'],
            defaults={'name': category_data['name']}
        )
        category_obj.shops.add(shop)

    # Очистка старых товаров магазина
    ProductInfo.objects.filter(shop=shop).delete()

    # Товары
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

        for param_name, param_value in item.get('parameters', {}).items():
            parameter_obj, _ = Parameter.objects.get_or_create(name=param_name)
            ProductParameter.objects.create(
                product_info=product_info,
                parameter=parameter_obj,
                value=param_value
            )
