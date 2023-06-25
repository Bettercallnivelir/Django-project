from io import TextIOWrapper
from csv import DictReader

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products
from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    # для вывода связи many-to-many
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description='Архивировать')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """Действие для админа(архивировать): меняем статус archived на True"""
    queryset.update(archived=True)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    # список действий для админа
    change_list_template = 'shopapp/products_changelist.html'
    actions = [
        mark_archived,
        'export_csv',
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    list_display = 'pk', 'name', 'price', 'description_short', 'archived', 'created_by',
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
        ("Images", {
            'fields': ('preview',),
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

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportForm()
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html', context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_products(
            form.files['csv_file'].file,
            encoding=request.encoding,
        )
        self.message_user(request, 'CSV was imported!')
        return redirect("..")
    
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                'import-products-csv/',
                self.import_csv,
                name='import_products_csv'
            )
        ]
        return new_urls + urls


# admin.site.register(Product, ProductAdmin)

# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = 'shopapp/order_changelist.html'
    inlines = [
        ProductInline,
    ]
    list_display = 'delivery_address', 'promocode', 'created', 'user_verbose'

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')

    def user_verbose(self, obj: Order):
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        """Метод для импорта csv-фала"""
        if request.method == 'GET':
            form = CSVImportForm()
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html', context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        csv_file = TextIOWrapper(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )
        reader = DictReader(csv_file)

        orders = [
            Order(**row)
            for row in reader
        ]
        print(orders)
        Order.objects.bulk_create(orders)
        self.message_user(request, 'Orders from CSV was imported!')
        return redirect('..')

    def get_urls(self):
        """Переопределяем метод для подключения к url(создаем новый адрес)"""
        urls = super().get_urls()
        new_urls = [
            path(
                'import-orders-csv/',
                self.import_csv,
                name='import_orders_csv'
            )
        ]
        return new_urls + urls
