from django import forms
from django.contrib.auth.models import User
from django.core import validators
from django.utils.translation import gettext_lazy
from .models import Product, Order


# class ProductForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     price = forms.DecimalField(min_value=3, max_value=99, decimal_places=3)
#     descriptions = forms.CharField(
#         widget=forms.Textarea(attrs={'rows': 5, 'cols': 5}),
#         label='Product description',
#         validators=[validators.RegexValidator(regex=r'great', message='Поле должно содержать слово "greate"')],
#     )

class ProductForm(forms.ModelForm):
    """Форма для модели Product"""
    class Meta:
        model = Product
        fields = 'name', 'price', 'descriptions', 'discount'


class OrderForm(forms.ModelForm):
    """Форма для модели Order"""
    class Meta:
        model = Order
        fields = 'user', 'delivery_address', 'promocode', 'products',
        labels = {
            'delivery_address': gettext_lazy('Адрес доставки'),
            'products': gettext_lazy('Выберите один или несколько продуктов'),
        }
        help_texts = {
            'delivery_address': gettext_lazy('Город, улица, номер дома'),
            'promocode': gettext_lazy('Необязательное поле')
        }
        widgets = {
            'delivery_address': forms.Textarea(attrs={'required': True}),
            'products': forms.CheckboxSelectMultiple,
        }

