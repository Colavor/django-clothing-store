from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField("Название категории", max_length=255)
    parent = models.ForeignKey(
        "self",
        verbose_name="Родительская категория",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Название товара", max_length=255)
    description = models.TextField("Описание", blank=True)
    base_price = models.DecimalField("Базовая цена", max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.CASCADE,
        related_name="products"
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        on_delete=models.CASCADE,
        related_name="variants"
    )
    size = models.CharField("Размер", max_length=10)
    color = models.CharField("Цвет", max_length=50)
    sku = models.CharField("Артикул", max_length=100, unique=True)

    class Meta:
        verbose_name = "Вариант товара"
        verbose_name_plural = "Варианты товара"
        unique_together = ("product", "size", "color")

    def __str__(self):
        return f"{self.product.name} ({self.size}, {self.color})"


class Stock(models.Model):
    variant = models.OneToOneField(
        ProductVariant,
        verbose_name="Вариант товара",
        on_delete=models.CASCADE,
        related_name="stock"
    )
    quantity = models.PositiveIntegerField("Количество на складе")
    min_stock = models.PositiveIntegerField("Минимальный остаток", default=0)

    class Meta:
        verbose_name = "Остаток на складе"
        verbose_name_plural = "Остатки на складе"

    def __str__(self):
        return f"Остаток: {self.variant} - {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "В ожидании"),
        ("paid", "Оплачен"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменен"),
    ]

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="orders"
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="pending")
    delivery_address = models.CharField("Адрес доставки", max_length=255)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ №{self.id}"

    def total_price(self):
        return sum(item.quantity * item.price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        on_delete=models.CASCADE,
        related_name="items"
    )
    variant = models.ForeignKey(
        ProductVariant,
        verbose_name="Вариант товара",
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField("Количество")
    price = models.DecimalField("Цена на момент покупки", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.variant} x {self.quantity}"