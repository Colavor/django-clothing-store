from django.contrib import admin
from .models import Category, Product, ProductVariant, Stock, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent")
    search_fields = ("name",)
    list_filter = ("parent",)
    list_display_links = ("id", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "base_price", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("name", "category__name")
    date_hierarchy = "created_at"
    inlines = [ProductVariantInline]
    list_display_links = ("id", "name")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "size", "color", "sku")
    search_fields = ("product__name", "sku", "color")
    list_filter = ("size", "color")
    raw_id_fields = ("product",)
    list_display_links = ("id", "sku")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("id", "variant", "quantity", "min_stock", "is_low")
    search_fields = ("variant__product__name",)
    raw_id_fields = ("variant",)

    @admin.display(description="Мало на складе?")
    def is_low(self, obj):
        return obj.quantity <= obj.min_stock


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "total_price_display")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "delivery_address")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    raw_id_fields = ("user",)
    readonly_fields = ("created_at",)
    list_display_links = ("id",)

    @admin.display(description="Общая сумма")
    def total_price_display(self, obj):
        return obj.total_price()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "variant", "quantity", "price")
    raw_id_fields = ("order", "variant")
    search_fields = ("variant__product__name",)