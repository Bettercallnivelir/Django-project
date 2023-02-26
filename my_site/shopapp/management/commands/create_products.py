from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """Создаём продукты в б.д."""

    def handle(self, *args, **options):
        self.stdout.write('Create products')
        products = [
            'Laptop',
            'Desktop',
            'Phone',
        ]
        for product_name in products:
            product, created = Product.objects.get_or_create(name=product_name)
            if created:
                self.stdout.write(f'Created product {product.name}')

        self.stdout.write(self.style.SUCCESS('Products created'))
