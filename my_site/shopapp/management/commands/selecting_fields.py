from django.core.management import BaseCommand
from django.contrib.auth.models import User

from shopapp.models import Product


class Command(BaseCommand):
    """Команда для выбора полей"""
    def handle(self, *args, **options):
        self.stdout.write('Start demo select fields')
        users_info = User.objects.values_list('pk', flat=True)
        for user_info in users_info:
            print(user_info)

        # products_values = Product.objects.values('pk', 'name')
        # for products_value in products_values:
        #     print(products_value)
            
        self.stdout.write('Done!')
