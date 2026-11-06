from django.test import SimpleTestCase
from django.urls import resolve

from shop.views import (
    CustomerCreate,
    add_to_cart,
    index,
    purchase,
    remove_from_cart,
    select_customer,
)


class UrlsTestCase(SimpleTestCase):
    def test_index_url(self):
        self.assertEqual(resolve("/").func, index)

    def test_customer_add_url(self):
        self.assertEqual(
            resolve("/customer/add/").func.view_class,
            CustomerCreate
        )

    def test_customer_select_url(self):
        self.assertEqual(
            resolve("/customer/select/").func,
            select_customer
        )

    def test_add_to_cart_url(self):
        self.assertEqual(
            resolve("/cart/add/1/").func,
            add_to_cart
        )

    def test_remove_from_cart_url(self):
        self.assertEqual(
            resolve("/cart/remove/0/").func,
            remove_from_cart
        )

    def test_buy_url(self):
        self.assertEqual(resolve("/buy/").func, purchase)
