# Diplom Backend — Marketplace API

Backend-часть дипломного проекта маркетплейса на Django + DRF.

## Стек технологий
- Python 3.10+
- Django 4.x
- Django REST Framework
- SQLite (dev)
- Token Authentication
- YAML (импорт прайсов)

---

## Реализованные функции

### Пользователи
- Регистрация пользователя
- Авторизация по Token
- Аутентификация через DRF

### Каталог
- Магазины
- Категории
- Товары
- Импорт прайса через YAML

### Корзина
- Добавление товаров
- Удаление товаров
- Поддержка товаров из разных магазинов

### Контакты
- Создание адресов доставки
- Удаление контактов

### Заказы
- Подтверждение заказа
- Привязка адреса доставки

---

## API Endpoints

### Аутентификация
- POST `/api/register/`
- POST `/api/login/`

### Каталог
- GET `/api/products/`

### Корзина
- GET `/api/cart/`
- POST `/api/cart/`
- DELETE `/api/cart/`

### Контакты
- GET `/api/contacts/`
- POST `/api/contacts/`
- DELETE `/api/contacts/`

### Заказы
- POST `/api/order/confirm/`

---

## Установка и запуск

```bash
git clone <repo>
cd diplom/orders
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

POST /api/partner/update/
Authorization: Token <token>
{
  "url": "https://example.com/shop.yaml"
}
