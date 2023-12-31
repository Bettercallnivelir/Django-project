from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, ngettext


def product_preview_directory_path(instance: 'Product', filename: str) -> str:
    return f'products/product_{instance.pk}/preview/{filename}'


class Product(models.Model):
    """
    Модель Product представляет товар в магазине

    Заказы: :model:`shopapp.Order`
    """
    name = models.CharField(max_length=100, db_index=True)
    descriptions = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, default=1)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shopapp:detail_product', kwargs={'pk': self.pk})

    # @property
    # def description_short(self):
    #     if len(self.descriptions) < 40:
    #         return self.descriptions
    #     return self.descriptions[:40] + '...'

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')


def product_images_directory_path(instance: 'ProductImage', filename: str) -> str:
    return f'products/product_{instance.product.pk}/{filename}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=100, null=False, blank=True)


class Order(models.Model):
    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=25, null=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name='orders')
    receipt = models.FileField(null=True, upload_to='orders/receipts/')

    def __str__(self):
        return f'Заказ №{self.pk}-{self.delivery_address}'

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
