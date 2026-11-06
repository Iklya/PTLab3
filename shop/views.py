
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.http import HttpResponseBadRequest
from django.db import transaction

from .models import Customer, Product, Purchase


def calculate_discount(total):
    """Рассчитывает скидку исключительно по сумме корзины."""
    if total >= 20000:
        return 10
    if total >= 10000:
        return 5
    if total >= 5000:
        return 3
    return 0


def get_cart(request):
    cart = request.session.get("cart", [])
    products = Product.objects.filter(id__in=cart)

    product_map = {product.id: product for product in products}

    cart_items = []
    total = 0

    for product_id in cart:
        product = product_map.get(product_id)

        if product is None:
            continue

        cart_items.append(product)
        total += product.price

    return cart_items, total


def index(request):
    products = Product.objects.all()
    customers = Customer.objects.all().order_by("name")

    selected_customer = None
    selected_customer_id = request.session.get("selected_customer_id")

    if selected_customer_id:
        selected_customer = Customer.objects.filter(
            id=selected_customer_id
        ).first()

        if selected_customer is None:
            request.session.pop("selected_customer_id", None)

    cart_items, cart_total = get_cart(request)
    discount_percent = calculate_discount(cart_total)
    discount_amount = cart_total * discount_percent // 100

    return render(
        request,
        "shop/index.html",
        {
            "products": products,
            "customers": customers,
            "selected_customer": selected_customer,
            "cart_items": cart_items,
            "cart_total": cart_total,
            "discount_percent": discount_percent,
            "discount_amount": discount_amount,
            "final_total": cart_total - discount_amount,
        }
    )


def select_customer(request):
    if request.method != "POST":
        return HttpResponseBadRequest()

    customer_id = request.POST.get("customer")

    if not customer_id:
        request.session.pop("selected_customer_id", None)
    else:
        customer = Customer.objects.filter(id=customer_id).first()

        if customer is None:
            return redirect("index")

        request.session["selected_customer_id"] = customer.id

    request.session.modified = True

    return redirect("index")


def add_to_cart(request, product_id):
    if request.method != "POST":
        return HttpResponseBadRequest()

    if not Product.objects.filter(id=product_id).exists():
        return redirect("index")

    cart = request.session.get("cart", [])
    cart.append(product_id)

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("index")


def remove_from_cart(request, index):
    if request.method != "POST":
        return HttpResponseBadRequest()

    cart = request.session.get("cart", [])

    if 0 <= index < len(cart):
        cart.pop(index)

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("index")


class CustomerCreate(CreateView):
    model = Customer
    fields = ["name", "address"]
    template_name = "shop/customer_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        # Автоматически выбираем только что созданного покупателя.
        self.request.session["selected_customer_id"] = self.object.id
        self.request.session.modified = True

        return response

    def get_success_url(self):
        return "/"


def purchase(request):
    cart_items, cart_total = get_cart(request)

    if not cart_items:
        return redirect("index")

    customer_id = request.session.get("selected_customer_id")

    customer = Customer.objects.filter(id=customer_id).first()

    if customer is None:
        request.session.pop("selected_customer_id", None)
        return redirect("index")

    if request.method == "GET":
        return render(
            request,
            "shop/purchase_form.html",
            {
                "customer": customer,
                "cart_items": cart_items,
                "cart_total": cart_total,
                "discount_percent": calculate_discount(cart_total),
            }
        )

    if request.method == "POST":
        discount_percent = calculate_discount(cart_total)
        discount_amount = cart_total * discount_percent // 100
        final_total = cart_total - discount_amount

        with transaction.atomic():
            for product in cart_items:
                Purchase.objects.create(
                    customer=customer,
                    product=product
                )

        request.session["cart"] = []
        request.session.modified = True

        return render(
            request,
            "shop/purchase_success.html",
            {
                "customer": customer,
                "cart_total": cart_total,
                "discount_percent": discount_percent,
                "discount_amount": discount_amount,
                "final_total": final_total,
                "cart_items": cart_items,
            }
        )

    return HttpResponseBadRequest()
