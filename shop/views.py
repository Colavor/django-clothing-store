from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum

from .models import Category, Order


def order_stats(request):
    # GET /shop/stats/orders/
    today = timezone.now().date()

    #количество оплаченных заказов за сегодня
    today_paid_qs = Order.paid.filter(created_at__date=today)
    agg_orders = today_paid_qs.aggregate(total_paid_orders=Count("id"))

    #общее количество купленных позиций по заказам за сегодня
    agg_items = today_paid_qs.aggregate(total_items=Sum("items__quantity"))

    #количество товаров в каждой категории
    category_qs = Category.objects.annotate(products_count=Count("products"))
    categories_info = ", ".join(f"{c.name}: {c.products_count} товаров" for c in category_qs)

    text = (
        f"Оплаченных заказов сегодня: {agg_orders['total_paid_orders'] or 0}\n"
        f"Всего купленных позиций сегодня: {agg_items['total_items'] or 0}\n"
        f"Товары по категориям: {categories_info or 'нет категорий'}"
    )

    return HttpResponse(text, content_type="text/plain; charset=utf-8")
