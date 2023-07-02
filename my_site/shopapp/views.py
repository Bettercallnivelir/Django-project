"""
Набор Views(представлений) для приложения shopapp.

Разные view интернет магазина: по товарам, заказам и т.д.
"""
import logging
from csv import DictWriter
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework.request import Request
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from shopapp.forms import ProductForm, OrderForm, GroupForm
from shopapp.models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer
from .common import save_csv_products

# Create your views here.
url_names = ['index', 'groups', 'products', 'orders']
log = logging.getLogger(__name__)


@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    ViewSet для класса Product
    Полный CRUD для сущности товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]
    ordering_fields = ['name', 'price']
    search_fields = ['name', 'descriptions']

    @extend_schema(
        summary='Get one product by ID',
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description='Empty response, product by id not found'),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @method_decorator(cache_page(60))
    def list(self, *args, **kwargs):
        print('CACHED')
        return super().list(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'descriptions',
            'price',
            'discount',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=['post'],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    """ViewSet для класса Order"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = [
        'delivery_address',
        'created',
    ]
    ordering_fields = ['pk', 'created', 'user']


class ShopIndexView(View):
    """View списка ссылок приложения"""

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'urls': url_names,
            'items': 23,
        }
        log.debug('Products for shop index: %s', context)
        log.info('Rendering shop index')
        print('shop index context', context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    """View списка групп"""

    def get(self, request):
        data = {
            'groups': Group.objects.prefetch_related('permissions').all(),
            'form': GroupForm(),
        }
        return render(request, 'shopapp/groups-list.html', context=data)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductsDetailsView(DetailView):
    """View детальное описание продукта"""
    # model = Product
    template_name = 'shopapp/product-details.html'
    queryset = Product.objects.prefetch_related('images')


class ProductListView(ListView):
    """View списка продуктов"""
    model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=True)


class CreateProductView(PermissionRequiredMixin, View):
    """View создяния продукта"""
    permission_required = 'shopapp.add_product'

    def get(self, request: HttpRequest):
        """Обработка Get-запроса. Получаем форму на создание продукта"""
        context = {
            'form': ProductForm()
        }
        return render(request, 'shopapp/create_product.html', context=context)

    def post(self, request: HttpRequest):
        """Обработка POST-запроса. Создаём продукт"""
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
        return redirect('shopapp:products')


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    """View Обновление деталей продукта"""
    model = Product
    # fields = 'name', 'price', 'preview',
    template_name_suffix = '_update_form'
    form_class = ProductForm

    def test_func(self):
        """Проверка прав на изменение продукта"""
        if self.request.user.is_superuser:
            return True
        if self.get_object().created_by == self.request.user and \
                self.request.user.has_perm('shopapp.change_product'):
            return True
        return False

    def get_success_url(self):
        return reverse('shopapp:detail_product', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    """View удаления продукта"""
    model = Product
    template_name_suffix = '_soft_delete'
    success_url = reverse_lazy('shopapp:products')

    def form_valid(self, form):
        """Меняем значение параметра 'archived'(софт-удаление)"""
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderListView(LoginRequiredMixin, ListView):
    """View вывод списка заказов из модели Order"""
    queryset = Order.objects.select_related('user').prefetch_related('products')


class OrderDetailView(PermissionRequiredMixin, DetailView):
    """View вывод детального описания заказа"""
    queryset = Order.objects.select_related('user').prefetch_related('products')
    permission_required = 'shopapp.view_order'


class OrderUpdateView(UpdateView):
    """View Обновление заказа"""
    model = Order
    form_class = OrderForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('shopapp:order_detail', kwargs={'pk': self.object.pk})


class OrderDeleteView(DeleteView):
    """View Удаление заказа"""
    model = Order
    success_url = reverse_lazy('shopapp:orders')


class OrderCreateView(CreateView):
    """View Создание заказа"""
    form_class = OrderForm
    template_name = 'shopapp/order_create.html'
    success_url = reverse_lazy('shopapp:orders')


class ProductsDataExportView(View):
    def get(self, request) -> JsonResponse:
        cache_key = 'Products_data_export'
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk')
            products_data = [
                {
                    'pk': product.pk,
                    'name': product.name,
                    'price': product.price,
                    'archived': product.archived,
                }
                for product in products
            ]
            cache.set('Products_data_export', products_data, 300)
        return JsonResponse({'products': products_data})


class OrdersDataExportView(UserPassesTestMixin, View):
    def get(self, request) -> JsonResponse:
        orders = Order.objects.select_related('user').prefetch_related('products')
        orders_data = [
            {
                'pk': order.pk,
                'promocode': order.promocode,
                'user': order.user.username,
                'products': [product.pk for product in order.products.all()]
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})

    def test_func(self):
        """Проверка пользователя на уровень доступа staff"""
        return self.request.user.is_staff


class LatestProductsFeed(Feed):
    title = "Shop products (latest)"
    description = 'Updates on changes and addition products'
    link = reverse_lazy('shopapp:products')

    def items(self):
        return Product.objects.order_by('-created')[:5]

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.descriptions[:100]


class UserOrdersListView(LoginRequiredMixin, ListView):
    """View списка заказов определенного пользователя"""
    login_url = reverse_lazy('myauth:login')
    owner = None

    def get_queryset(self):
        self.owner = get_object_or_404(User, id=self.kwargs['user_id'])
        orders = Order.objects.select_related('user').filter(user=self.owner.pk).prefetch_related('products')
        return orders

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


def export_orders(request: HttpRequest, user_id):
    """Функция экспорта данных о заказе выбранного пользователя с кэшированием"""
    owner = get_object_or_404(User, id=user_id)
    cache_key = f'Orders_data_export_for_user_{owner.pk}'
    orders_data = cache.get(cache_key)
    if orders_data is None:
        orders = Order.objects.select_related('user').filter(user=owner.pk).prefetch_related('products')
        orders_data = [
            {
                'pk': order.pk,
                'promocode': order.promocode,
                'products': [product.name for product in order.products.all()]
            }
            for order in orders
        ]
        cache.set(cache_key, orders_data, 300)
    return JsonResponse({'orders': orders_data})
