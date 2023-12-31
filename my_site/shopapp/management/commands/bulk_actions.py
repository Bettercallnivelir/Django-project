from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """Команда для выбора полей"""

    def handle(self, *args, **options):
        self.stdout.write('Start demo bulk actions')
        # info = [
        #     ('Smartphone 1', 199),
        #     ('Smartphone 2', 299),
        #     ('Smartphone 3', 399),
        # ]
        # products = [Product(name=name, price=price) for name, price in info]
        # result = Product.objects.bulk_create(products)
        # for obj in result:
        #     print(obj)

        result = Product.objects.filter(
            name__contains='Smartphone').update(discount=33)
        print(result)

        self.stdout.write('Done!')
