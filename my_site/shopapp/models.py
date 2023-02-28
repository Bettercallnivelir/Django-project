from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=100)
    descriptions = models.TextField(null=False, blank=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    # @property
    # def description_short(self):
    #     if len(self.descriptions) < 40:
    #         return self.descriptions
    #     return self.descriptions[:40] + '...'


class Order(models.Model):
    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=25, null=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name='orders')

    def __str__(self):
        return f'Заказ №{self.pk}-{self.delivery_address}'
