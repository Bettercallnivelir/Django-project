from django.core.management import BaseCommand
from django.db.models import Avg, Max, Min, Count, Sum

from shopapp.models import Product, Order


class Command(BaseCommand):
    """Команда для выбора полей"""
    def handle(self, *args, **options):
        self.stdout.write('Start demo aggregate')

        # result = Product.objects.aggregate(
        #     Avg('price'),
        #     Min('price'),
        #     Max('price'),
        #     count=Count('pk')
        # )
        # print(result)

        orders = Order.objects.annotate(
            total=Sum('products__price'),
            products_count=Count('products'),
        )
        for order in orders:
            print(f'Order #{order.id} with {order.products_count} products, total worth: {order.total}')

        self.stdout.write('Done!')
