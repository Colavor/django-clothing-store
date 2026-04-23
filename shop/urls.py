from django.urls import path

from . import views


urlpatterns = [
    path("", views.shop_home, name="shop_home"),
    path("demo/create/", views.create_product, name="create_product"),
    path("demo/update/<int:pk>/", views.update_product, name="update_product"),
    path("demo/delete/<int:pk>/", views.delete_product, name="delete_product"),
    path("demo/category/create/", views.create_category, name="create_category"),
    path("demo/category/update/<int:pk>/", views.update_category, name="update_category"),
    path("demo/category/delete/<int:pk>/", views.delete_category, name="delete_category"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<int:pk>/", views.category_detail, name="category_detail"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/pdf/", views.product_pdf, name="product_pdf"),
    path("demo/orders-select/", views.orders_with_users, name="orders_with_users"),
    path("demo/categories-prefetch/", views.categories_with_products, name="categories_with_products"),
    path("demo/queryset/", views.queryset_demo, name="queryset_demo"),
]

