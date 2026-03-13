from django.urls import path

from . import views


urlpatterns = [
    path("", views.shop_index, name="shop_index"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("stats/orders/", views.order_stats, name="order_stats"),
]

