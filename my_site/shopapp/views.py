from timeit import default_timer

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


# Create your views here.

def shop_index(request: HttpRequest):
    products = [
        ('laptop', 1900.99),
        ('desktop', 2900.36),
        ('phone', 900.63),
    ]
    context = {'time_running': default_timer(),
               'products': products,
               }
    return render(request, 'shopapp/shop-index.html', context=context)
