from timeit import default_timer

from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpRequest

from shopapp.forms import ProductForm, OrderForm
from shopapp.models import Product, Order

# Create your views here.
url_names = ['index', 'groups', 'products', 'orders']


def shop_index(request: HttpRequest):
    context = {
        'urls': url_names,
    }
    return render(request, 'shopapp/shop-index.html', context=context)


def groups_list(request: HttpRequest):
    data = {
        'groups': Group.objects.prefetch_related('permissions').all()
    }
    return render(request, 'shopapp/groups-list.html', context=data)


def products_list(request: HttpRequest):
    data = {
        'products': Product.objects.all()
    }
    return render(request, 'shopapp/products-list.html', context=data)


def orders_list(request: HttpRequest):
    data = {
        'orders': Order.objects.select_related('user').prefetch_related('products').all()
    }
    return render(request, 'shopapp/orders-list.html', context=data)


def create_product(request: HttpRequest):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # Product.objects.create(**form.cleaned_data) # если форма не связана с моделью
            form.save()
            url = reverse('shopapp:products')
            return redirect(url)
    else:
        form = ProductForm()

    context = {
        'form': form
    }

    return render(request, 'shopapp/create_product.html', context=context)


def create_order(request: HttpRequest):
    """Функция создания заказа через форму OrderForm"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = User.objects.first()
            form.save()
            url = reverse('shopapp:orders')
            return redirect(url)
    else:
        form = OrderForm()

    context = {
        'form': form
    }

    return render(request, 'shopapp/create_order.html', context=context)
