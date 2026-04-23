from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


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
    is_promo = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.CASCADE,
        related_name="products"
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    tags = models.ManyToManyField(
        "ProductTag",
        through="ProductTagLink",
        related_name="products",
        verbose_name="Теги",
        blank=True,
    )
    pdf_file = models.FileField(
        "PDF",
        upload_to="products/pdfs/",
        blank=True,
        null=True,
    )
    product_url = models.URLField("Ссылка на товар", blank=True)
    image = models.ImageField("Изображение", upload_to="products/images/", blank=True, null=True)
    manual = models.FileField("Файл", upload_to="products/files/", blank=True, null=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.pk])


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


class ProductTag(models.Model):
    name = models.CharField("Название тега", max_length=50, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class ProductTagLink(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    tag = models.ForeignKey(ProductTag, on_delete=models.CASCADE)
    added_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Связь товара и тега"
        verbose_name_plural = "Связи товара и тегов"

# оплаченных заказов
class PaidOrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status="paid")


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
    paid_at = models.DateTimeField("Дата оплаты", null=True, blank=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="pending")
    delivery_address = models.CharField("Адрес доставки", max_length=255)

    objects = models.Manager()
    paid = PaidOrderManager()

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ №{self.id}"

    def total_price(self):
        return sum(item.quantity * item.price for item in self.items.all())
    #оплатить заказ
    def mark_as_paid(self):
        self.paid_at = timezone.now()
        self.status = "paid"
        self.save()
    #получить заказы за сегодня
    @classmethod
    def for_today(cls):
        today = timezone.now().date()
        return cls.objects.filter(created_at__date=today)


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

#дороже 5000 созданные в этом году
def get_expensive_recent_products():
    current_year = timezone.now().year
    return Product.objects.filter(
        base_price__gt=5000,
        created_at__year=current_year,
    )

#все заказы пользователя, кроме отменённых.
def get_user_orders_without_cancelled(user):
    return user.orders.exclude(status="cancelled")

#ссылка на страницу товара
def get_product_detail_url(product):
    return product.get_absolute_url()