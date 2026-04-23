from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from xhtml2pdf import pisa
import os
from django.conf import settings
from django.template.loader import get_template

from .models import Category, Order, Product


def shop_home(request):
    return render(request, "shop/home.html")



def create_product(request):
    categories = Category.objects.all().order_by("name")
    if not categories.exists():
        Category.objects.create(name="Demo категория")
        categories = Category.objects.all().order_by("name")

    if request.method == "POST":
        name = request.POST.get("name", "Demo товар").strip() or "Demo товар"
        description = request.POST.get("description", "").strip()
        category_id = request.POST.get("category_id")
        base_price_raw = request.POST.get("base_price", "1000").strip()
        product_url = request.POST.get("product_url", "").strip()
        image = request.FILES.get("image")

        try:
            base_price = float(base_price_raw)
        except ValueError:
            base_price = 1000

        category = Category.objects.filter(pk=category_id).first()
        if category is None:
            category = categories.first()

        product = Product.objects.create(
            name=name,
            description=description,
            base_price=base_price,
            category=category,
            product_url=product_url,
            image=image,
        )
        return redirect("product_detail", pk=product.id)

    return render(request, "shop/product/create.html", {"categories": categories})


def update_product(request, pk: int):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return redirect("product_list")

    categories = Category.objects.all().order_by("name")

    if request.method == "POST":
        name = request.POST.get("name", product.name).strip() or product.name
        description = request.POST.get("description", "").strip()
        base_price_raw = request.POST.get("base_price", str(product.base_price)).strip()
        try:
            base_price = float(base_price_raw)
        except ValueError:
            base_price = product.base_price

        category_id = request.POST.get("category_id")
        category = Category.objects.filter(pk=category_id).first() or product.category
        Product.objects.filter(pk=product.pk).update(
            name=name,
            description=description,
            base_price=base_price,
            category=category,
        )
        return redirect("product_detail", pk=product.id)

    return render(
        request,
        "shop/product/update.html",
        {"product": product, "categories": categories},
    )


def delete_product(request, pk: int):
    # POST /shop/demo/delete/<id>/
    if not Product.objects.filter(pk=pk).exists():
        return redirect("product_list")

    if request.method == "POST":
        Product.objects.filter(pk=pk).delete()
    return redirect("product_list")


def create_category(request):
    c = Category.objects.create(name="Категория (demo)")
    return redirect("category_detail", pk=c.id)


def update_category(request, pk: int):
    try:
        c = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return redirect("category_list")
    c.name = f"{c.name} (обновлена)"
    c.save()
    return redirect("category_detail", pk=c.id)


def delete_category(request, pk: int):
    try:
        c = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return redirect("category_list")
    c.delete()
    return redirect("category_list")


def category_list(request):
    categories = Category.objects.all().order_by("id")
    return render(request, "shop/category/list.html", {"categories": categories})


def category_detail(request, pk: int):
    try:
        c = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return HttpResponse("Категория не найдена", status=404, content_type="text/plain; charset=utf-8")
    parent = c.parent_id or "—"
    return HttpResponse(f"id={c.id}\nname={c.name}\nparent_id={parent}", content_type="text/plain; charset=utf-8")


def product_list(request):
    query = request.GET.get("q", "").strip()
    mode = request.GET.get("mode", "icontains")

    products = Product.objects.select_related("category").all().order_by("id")
    if query:
        if mode == "contains":
            products = products.filter(name__contains=query)
        else:
            mode = "icontains"
            products = products.filter(name__icontains=query)

    stats = {
        "count": products.count(),
        "exists": products.exists(),
        "values": list(products.values("id", "name")[:5]),
        "values_list": list(products.values_list("id", "name")[:5]),
        "query": query,
        "mode": mode,
    }
    return render(request, "shop/product/list.html", {"products": products, "stats": stats})


def product_detail(request, pk: int):
    try:
        p = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return HttpResponse("Товар не найден", status=404, content_type="text/plain; charset=utf-8")
    return render(request, "shop/product/detail.html", {"product": p})

def link_callback(uri, rel):
    if uri.startswith("/static/"):
        return os.path.join(settings.BASE_DIR, "static", uri.replace("/static/", "", 1))
    return uri

#http://127.0.0.1:8000/shop/products/1/pdf/
def product_pdf(request, pk):
    product = get_object_or_404(Product, pk=pk)
    template = get_template("shop/product/pdf.html")
    html = template.render({"product": product})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="product.pdf"'
    pisa.CreatePDF(html, dest=response, link_callback=link_callback, encoding="utf-8")

    return response


def orders_with_users(request):
    # GET /shop/demo/orders-select/
    orders = Order.objects.select_related("user")
    lines = [f"Заказ {o.id}: пользователь {o.user.username}" for o in orders]
    return HttpResponse("\n".join(lines) or "Нет заказов", content_type="text/plain; charset=utf-8")


def categories_with_products(request):
    # GET /shop/demo/categories-prefetch/
    categories = Category.objects.prefetch_related("products")
    lines = []
    for c in categories:
        product_names = ", ".join(p.name for p in c.products.all())
        lines.append(f"{c.name}: {product_names or 'нет товаров'}")
    return HttpResponse("\n".join(lines) or "Нет категорий", content_type="text/plain; charset=utf-8")


def queryset_demo(request):
    name_icontains_count = Product.objects.filter(name__icontains="demo").count()
    name_contains_count = Product.objects.filter(name__contains="Demo").count()
    values_data = list(Product.objects.values("id", "name")[:3])
    values_list_data = list(Product.objects.values_list("id", "name")[:3])
    exists_demo = Product.objects.filter(name__icontains="demo").exists()
    updated = Product.objects.filter(pk__lt=0).update(description="noop")
    deleted, _ = Product.objects.filter(pk__lt=0).delete()

    return HttpResponse(
        "\n".join(
            [
                f"icontains_count={name_icontains_count}",
                f"contains_count={name_contains_count}",
                f"values={values_data}",
                f"values_list={values_list_data}",
                f"count={Product.objects.count()}",
                f"exists={exists_demo}",
                f"update={updated}",
                f"delete={deleted}",
            ]
        ),
        content_type="text/plain; charset=utf-8",
    )
