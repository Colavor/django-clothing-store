from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import HttpResponse
from .models import (
    Category,
    Order,
    OrderItem,
    Product,
    ProductTag,
    ProductTagLink,
    ProductVariant,
    Stock,
)

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class ProductTagLinkInline(admin.TabularInline):
    model = ProductTagLink
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent")
    search_fields = ("name",)
    list_filter = ("parent",)
    list_display_links = ("id", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "base_price", "created_at", "pdf_link")
    list_filter = ("category", "created_at")
    search_fields = ("name", "category__name")
    date_hierarchy = "created_at"
    inlines = [ProductVariantInline, ProductTagLinkInline]
    list_display_links = ("id", "name")
    actions = ["mark_as_promo", "unmark_as_promo", "generate_pdf_action"]

    @admin.action(description="Сделать акцией")
    def mark_as_promo(self, request, queryset):
        queryset.update(is_promo=True)

    @admin.action(description="Убрать из акции")
    def unmark_as_promo(self, request, queryset):
        queryset.update(is_promo=False)

    @admin.display(description="PDF")
    def pdf_link(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{0}">Скачать</a>', obj.pdf_file.url)
        return "-"

    @admin.action(description="Сгенерировать PDF документ для выбранных товаров")
    def generate_pdf_action(self, request, queryset):
        try:
            from weasyprint import HTML as WeasyHTML
        except Exception:
            self.message_user(request, "WeasyPrint недоступен на этом окружении.", level=messages.ERROR)
            return

        generated = 0
        for product in queryset:
            html = render_to_string("shop/product/pdf.html", {"product": product, "request": request})
            pdf_bytes = WeasyHTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf()
            file_name = f"product_{product.id}.pdf"
            product.pdf_file.save(file_name, ContentFile(pdf_bytes), save=True)
            generated += 1

        self.message_user(request, f"PDF сгенерирован: {generated} шт.")


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


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(ProductTagLink)
class ProductTagLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "tag", "added_at")
    raw_id_fields = ("product", "tag")
    search_fields = ("tag__name", "product__name")