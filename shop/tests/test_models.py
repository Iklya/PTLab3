from datetime import datetime

from django.test import TestCase

from shop.models import Customer, Product, Purchase


class ProductTestCase(TestCase):
    def setUp(self):
        self.book = Product.objects.create(name="Книга", price=740)
        self.pen = Product.objects.create(name="Ручка", price=50)

    def test_products_are_created(self):
        self.assertEqual(Product.objects.count(), 2)

    def test_product_names_are_correct(self):
        self.assertEqual(self.book.name, "Книга")
        self.assertEqual(self.pen.name, "Ручка")

    def test_product_prices_are_correct(self):
        self.assertEqual(self.book.price, 740)
        self.assertEqual(self.pen.price, 50)

    def test_product_str_returns_name(self):
        self.assertEqual(str(self.book), "Книга")

    def test_product_name_is_string(self):
        self.assertIsInstance(self.book.name, str)

    def test_product_price_is_int(self):
        self.assertIsInstance(self.book.price, int)


class CustomerTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Иванов",
            address="ул. Светлая, 1"
        )

    def test_customer_is_created(self):
        self.assertEqual(Customer.objects.count(), 1)

    def test_customer_name_and_address(self):
        self.assertEqual(self.customer.name, "Иванов")
        self.assertEqual(self.customer.address, "ул. Светлая, 1")

    def test_customer_str_returns_name(self):
        self.assertEqual(str(self.customer), "Иванов")

    def test_total_spent_is_zero_without_purchases(self):
        self.assertEqual(self.customer.total_spent(), 0)

    def test_total_spent_sums_purchase_prices(self):
        p1 = Product.objects.create(name="A", price=1000)
        p2 = Product.objects.create(name="B", price=2500)

        Purchase.objects.create(customer=self.customer, product=p1)
        Purchase.objects.create(customer=self.customer, product=p2)

        self.assertEqual(self.customer.total_spent(), 3500)

    def test_customer_purchase_count(self):
        product = Product.objects.create(name="A", price=100)

        Purchase.objects.create(customer=self.customer, product=product)
        Purchase.objects.create(customer=self.customer, product=product)

        self.assertEqual(self.customer.purchases.count(), 2)


class PurchaseTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Петров",
            address="ул. Лесная, 5"
        )
        self.product = Product.objects.create(name="Книга", price=740)
        self.purchase = Purchase.objects.create(
            customer=self.customer,
            product=self.product
        )

    def test_purchase_is_created(self):
        self.assertEqual(Purchase.objects.count(), 1)

    def test_purchase_customer(self):
        self.assertEqual(self.purchase.customer, self.customer)
        self.assertEqual(self.purchase.customer.name, "Петров")

    def test_purchase_product(self):
        self.assertEqual(self.purchase.product, self.product)
        self.assertEqual(self.purchase.product.name, "Книга")

    def test_purchase_date_is_datetime(self):
        self.assertIsInstance(self.purchase.date, datetime)

    def test_purchase_str_contains_customer_and_product(self):
        self.assertEqual(str(self.purchase), "Петров: Книга")

    def test_purchase_cascade_on_customer_delete(self):
        self.customer.delete()
        self.assertEqual(Purchase.objects.count(), 0)

    def test_purchase_cascade_on_product_delete(self):
        self.product.delete()
        self.assertEqual(Purchase.objects.count(), 0)

    def test_related_name_purchases(self):
        self.assertIn(self.purchase, self.customer.purchases.all())

    def test_str_methods(self):
        product = Product.objects.create(name="X", price=1)
        customer = Customer.objects.create(name="Y", address="Z")
        purchase = Purchase.objects.create(
            customer=customer,
            product=product
        )

        self.assertEqual(str(product), "X")
        self.assertEqual(str(customer), "Y")
        self.assertEqual(str(purchase), "Y: X")
