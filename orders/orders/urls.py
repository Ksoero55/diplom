"""
URL configuration for orders project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from backend.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    # path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('products/', ProductsListAPIView.as_view()),
    path('cart/', CartAPIView.as_view()),
    path('contacts/', ContactsAPIView.as_view()),
    path('confirm_order/', ConfirmOrderAPIView.as_view()),
    path('orders/', OrdersListAPIView.as_view()),
    path('register/', RegisterView.as_view()),
    path('confirm/<uid>/<token>/', ConfirmEmailView.as_view()),
]
