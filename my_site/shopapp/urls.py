from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import GroupsListView, OrderListView, ShopIndexView, \
    ProductsDetailsView, ProductListView, OrderDetailView, CreateProductView, ProductUpdateView, ProductDeleteView, \
    OrderUpdateView, OrderDeleteView, OrderCreateView, ProductsDataExportView, OrdersDataExportView, ProductViewSet,\
    OrderViewSet, LatestProductsFeed

app_name = 'shopapp'
routers = DefaultRouter()
routers.register('products', ProductViewSet)
routers.register('orders', OrderViewSet)

urlpatterns = [
    path('', ShopIndexView.as_view(), name='index'),
    path('groups/', GroupsListView.as_view(), name='groups'),
    path('products/', ProductListView.as_view(), name='products'),
    path('products/create/', CreateProductView.as_view(), name='create_product'),
    path('products/export/', ProductsDataExportView.as_view(), name='products-export'),
    path('orders/export/', OrdersDataExportView.as_view(), name='orders-export'),
    path('products/<int:pk>', ProductsDetailsView.as_view(), name='detail_product'),
    path('products/<int:pk>/update', ProductUpdateView.as_view(), name='update_product'),
    path('products/<int:pk>/delete', ProductDeleteView.as_view(), name='delete_product'),
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/update', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/create/', OrderCreateView.as_view(), name='create_order'),
    path('api/', include(routers.urls)),
    path('products/latest/feed/', LatestProductsFeed(), name='products-feed')
]
