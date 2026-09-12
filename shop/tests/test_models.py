from datetime import datetime

from django.test import TestCase

from shop.models import Customer, Product, Purchase


class ProductTestCase(TestCase):
    def setUp(self):
        self.book = Product.objects.create(name="Книга", price=740)
        self.pen = Product.objects.create(name="Ручка", price=50)

    def test_products_are_created(self):
        """Создаются оба товара."""
        self.assertEqual(Product.objects.count(), 2)

    def test_product_names_are_correct(self):
        """Имена товаров сохраняются как заданы."""
        self.assertEqual(self.book.name, "Книга")
        self.assertEqual(self.pen.name, "Ручка")

    def test_product_prices_are_correct(self):
        """Цены товаров сохраняются как заданы."""
        self.assertEqual(self.book.price, 740)
        self.assertEqual(self.pen.price, 50)

    def test_product_str_returns_name(self):
        """__str__ товара возвращает его имя."""
        self.assertEqual(str(self.book), "Книга")

    def test_product_name_is_string(self):
        """Имя товара — строка."""
        self.assertIsInstance(self.book.name, str)

    def test_product_price_is_int(self):
        """Цена товара — целое число."""
        self.assertIsInstance(self.book.price, int)


class CustomerTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Иванов",
            address="ул. Светлая, 1"
        )

    def test_customer_is_created(self):
        """Покупатель создаётся."""
        self.assertEqual(Customer.objects.count(), 1)

    def test_customer_name_and_address(self):
        """Имя и адрес сохраняются."""
        self.assertEqual(self.customer.name, "Иванов")
        self.assertEqual(self.customer.address, "ул. Светлая, 1")

    def test_customer_str_returns_name(self):
        """__str__ покупателя возвращает имя."""
        self.assertEqual(str(self.customer), "Иванов")

    def test_total_spent_is_zero_without_purchases(self):
        """Без покупок сумма = 0."""
        self.assertEqual(self.customer.total_spent(), 0)

    def test_no_discount_without_purchases(self):
        """Без покупок скидки нет."""
        self.assertEqual(self.customer.discount_percent(), 0)
        self.assertEqual(self.customer.discount_amount(), 0)

    def test_total_with_discount_equals_total_without_purchases(self):
        """Итог без покупок = 0."""
        self.assertEqual(self.customer.total_with_discount(), 0)

    def test_total_spent_sums_purchase_prices(self):
        """total_spent суммирует стоимость покупок."""
        p1 = Product.objects.create(name="A", price=1000)
        p2 = Product.objects.create(name="B", price=2500)
        Purchase.objects.create(customer=self.customer, product=p1)
        Purchase.objects.create(customer=self.customer, product=p2)
        self.assertEqual(self.customer.total_spent(), 3500)

    def test_discount_zero_below_5000(self):
        """Ниже 5000 — скидка 0%."""
        p = Product.objects.create(name="A", price=4999)
        Purchase.objects.create(customer=self.customer, product=p)
        self.assertEqual(self.customer.discount_percent(), 0)

    def test_discount_three_percent_from_5000(self):
        """От 5000 — скидка 3%."""
        p = Product.objects.create(name="A", price=5000)
        Purchase.objects.create(customer=self.customer, product=p)
        self.assertEqual(self.customer.discount_percent(), 3)

    def test_discount_five_percent_from_10000(self):
        """От 10000 — скидка 5%."""
        p = Product.objects.create(name="A", price=10000)
        Purchase.objects.create(customer=self.customer, product=p)
        self.assertEqual(self.customer.discount_percent(), 5)

    def test_discount_ten_percent_from_20000(self):
        """От 20000 — скидка 10%."""
        p = Product.objects.create(name="A", price=20000)
        Purchase.objects.create(customer=self.customer, product=p)
        self.assertEqual(self.customer.discount_percent(), 10)

    def test_discount_amount_matches_percent(self):
        """discount_amount = total * percent / 100."""
        p = Product.objects.create(name="A", price=10000)
        Purchase.objects.create(customer=self.customer, product=p)
        self.assertEqual(self.customer.discount_amount(), 500)

    def test_total_with_discount_after_purchase(self):
        """total_with_discount = total - discount_amount."""
        p = Product.objects.create(name="A", price=10000)
        Purchase.objects.create(customer=self.customer, product=p)
        self.assertEqual(self.customer.total_with_discount(), 9500)

    def test_discount_grows_with_second_purchase(self):
        """Скидка пересчитывается после второй покупки."""
        p1 = Product.objects.create(name="A", price=5000)
        p2 = Product.objects.create(name="B", price=6000)
        Purchase.objects.create(customer=self.customer, product=p1)
        self.assertEqual(self.customer.discount_percent(), 3)
        Purchase.objects.create(customer=self.customer, product=p2)
        self.assertEqual(self.customer.discount_percent(), 5)

    def test_customer_purchase_count(self):
        """Количество покупок покупателя."""
        p = Product.objects.create(name="A", price=100)
        Purchase.objects.create(customer=self.customer, product=p)
        Purchase.objects.create(customer=self.customer, product=p)
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
        """Покупка создаётся."""
        self.assertEqual(Purchase.objects.count(), 1)

    def test_purchase_customer(self):
        """Покупка связана с покупателем."""
        self.assertEqual(self.purchase.customer, self.customer)
        self.assertEqual(self.purchase.customer.name, "Петров")

    def test_purchase_product(self):
        """Покупка связана с товаром."""
        self.assertEqual(self.purchase.product, self.product)
        self.assertEqual(self.purchase.product.name, "Книга")

    def test_purchase_date_is_datetime(self):
        """Дата покупки — datetime."""
        self.assertIsInstance(self.purchase.date, datetime)

    def test_purchase_str_contains_customer_and_product(self):
        """__str__ покупки содержит имя покупателя и товар."""
        self.assertEqual(str(self.purchase), "Петров: Книга")

    def test_purchase_cascade_on_customer_delete(self):
        """Удаление покупателя удаляет его покупки."""
        self.customer.delete()
        self.assertEqual(Purchase.objects.count(), 0)

    def test_purchase_cascade_on_product_delete(self):
        """Удаление товара удаляет связанные покупки."""
        self.product.delete()
        self.assertEqual(Purchase.objects.count(), 0)

    def test_related_name_purchases(self):
        """related_name='purchases' работает."""
        self.assertIn(self.purchase, self.customer.purchases.all())

    def test_str_methods(self):
        """__str__ у всех моделей возвращает имена."""
        p = Product.objects.create(name="X", price=1)
        c = Customer.objects.create(name="Y", address="Z")
        pur = Purchase.objects.create(customer=c, product=p)
        self.assertEqual(str(p), "X")
        self.assertEqual(str(c), "Y")
        self.assertEqual(str(pur), "Y: X")

    def test_boundary_discounts(self):
        """Границы скидок: 4999/5000/9999/10000/19999/20000."""
        c = Customer.objects.create(name="A", address="B")
        for price, expected in [(4999, 0), (5000, 3), (9999, 3),
                                (10000, 5), (19999, 5), (20000, 10)]:
            Purchase.objects.all().delete()
            p = Product.objects.create(name=f"p{price}", price=price)
            Purchase.objects.create(customer=c, product=p)
            self.assertEqual(c.discount_percent(), expected, f"price={price}")
