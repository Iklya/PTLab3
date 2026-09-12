from django.test import SimpleTestCase
from django.urls import resolve

from shop.views import CustomerCreate, PurchaseCreate, index


class UrlsTestCase(SimpleTestCase):

    def test_index_url(self):
        """Маршрут '/' ведёт на index."""
        self.assertEqual(resolve('/').func, index)

    def test_customer_add_url(self):
        """Маршрут '/customer/add/' ведёт на CustomerCreate."""
        self.assertEqual(
            resolve('/customer/add/').func.view_class,
            CustomerCreate
        )

    def test_buy_url(self):
        """Маршрут '/buy/' ведёт на PurchaseCreate."""
        self.assertEqual(
            resolve('/buy/').func.view_class,
            PurchaseCreate
        )
