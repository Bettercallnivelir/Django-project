from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product


class Command(BaseCommand):
    """Создаём заказ в б.д."""

    @transaction.atomic()
    def handle(self, *args, **options):
        self.stdout.write('Create order with products')
        user = User.objects.get(username='admin')
        products: Sequence[Product] = Product.objects.defer('descriptions', 'price', 'created').all()
        order, created = Order.objects.get_or_create(
            delivery_address='Minesota, 12st.',
            promocode='ZERO',
            user=user,
        )
        for product in products[:2]:
            order.products.add(product)
        order.save()
        self.stdout.write(f'Created order {order}')
