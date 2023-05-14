from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from shopapp.forms import ProductForm, OrderForm, GroupForm
from shopapp.models import Product, Order, ProductImage

# Create your views here.
url_names = ['index', 'groups', 'products', 'orders']


class ShopIndexView(View):
    """View списка ссылок приложения"""

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'urls': url_names,
            'items': 23,
        }
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
