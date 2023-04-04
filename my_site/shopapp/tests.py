from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.test import TestCase
from django.conf import settings

from .models import Product, Order
from string import ascii_letters
from random import choices


class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='Vtest', password='test111')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.user.user_permissions.add(25)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)
        self.product_name = ''.join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_product_create(self):
        response = self.client.post(
            reverse('shopapp:create_product'),
            {
                'name': self.product_name,
                'price': '3.55',
                'discount': '12',
            }
        )

        self.assertRedirects(response, reverse('shopapp:products'))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='Vtest', password='test111')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.product = Product.objects.create(name='RTL')

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    def test_get_product(self):
        response = self.client.get(
            reverse('shopapp:detail_product', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse('shopapp:detail_product', kwargs={'pk': self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Vtest', password='test111')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_products_list(self):
        response = self.client.get(reverse('shopapp:products'))
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=True),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/product_list.html')


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='Vtest', password='test111')
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:orders'))
        self.assertContains(response, 'Orders')

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'users-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse('shopapp:products-export'))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk')
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': str(product.price),
                'archived': product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data['products'],
            expected_data,
        )


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='Some user', password='test111')
        cls.user = User.objects.create_user(**cls.credentials)
        permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)
        self.order = Order.objects.create(
            delivery_address='some address',
            promocode='test',
            user=self.user
        )

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse('shopapp:order_detail', kwargs={'pk': self.order.pk})
        )
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context['object'].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        "order-fixture.json",
    ]

    @classmethod
    def setUpClass(cls):
        """Создаём пользователя и даём статус staff"""
        cls.credentials = dict(username='Some user', password='test123', is_staff=True)
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    def test_get_orders_view(self):
        response = self.client.get(reverse('shopapp:orders-export'))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.select_related('user').prefetch_related('products')
        expected_data = [
            {
                'pk': order.pk,
                'promocode': order.promocode,
                'user': order.user.username,
                'products': [product.pk for product in order.products.all()]
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(orders_data['orders'], expected_data)
