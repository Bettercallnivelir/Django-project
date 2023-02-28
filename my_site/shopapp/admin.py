from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Product, Order
from .admin_mixins import ExportAsCSVMixin


class OrderInline(admin.TabularInline):
    # для вывода связи many-to-many
    model = Product.orders.through


@admin.action(description='Архивировать')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """Действие для админа(архивировать): меняем статус archived на True"""
    queryset.update(archived=True)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    # список действий для админа
    actions = [
        mark_archived,
        'export_csv',
    ]
    inlines = [
        OrderInline,
    ]
    list_display = 'pk', 'name', 'price', 'description_short', 'archived'
    list_display_links = 'name', 'pk'
    search_fields = ('name', 'price')
    # Секции для полей Product
    fieldsets = [
        (None, {
            'fields': ('name', 'descriptions',)
        }),
        ("Price options", {
            'fields': ('price', 'discount'),
            'classes': ('wide', 'collapse'),
        }),
        ('Extra options', {
            'fields': ('archived',),
            'classes': ('collapse',),
            'description': 'Only for superuser!!!'
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.descriptions) < 40:
            return obj.descriptions
        return obj.descriptions[:40] + '...'


# admin.site.register(Product, ProductAdmin)

# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]
    list_display = 'delivery_address', 'promocode', 'created', 'user_verbose'

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')

    def user_verbose(self, obj: Order):
        return obj.user.first_name or obj.user.username
