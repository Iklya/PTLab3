
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path(
        "customer/add/",
        views.CustomerCreate.as_view(),
        name="customer_add"
    ),

    path(
        "customer/select/",
        views.select_customer,
        name="select_customer"
    ),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/remove/<int:index>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "buy/",
        views.purchase,
        name="buy"
    ),
]
