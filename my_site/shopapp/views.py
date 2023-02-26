from timeit import default_timer

from django.contrib.auth.models import Group
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

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
