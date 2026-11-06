from django.test import TestCase
from django.urls import reverse

from shop.models import Customer, Product, Purchase
from shop.views import calculate_discount


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.book = Product.objects.create(name="Книга", price=740)
        self.customer = Customer.objects.create(
            name="Иванов",
            address="ул. Светлая, 1"
        )

    def test_index_returns_200(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "shop/index.html")

    def test_index_contains_product_name(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Книга")

    def test_index_contains_customer_name(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Иванов")

    def test_index_context_has_products(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(list(response.context["products"]), [self.book])

    def test_index_context_has_customers(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(
            list(response.context["customers"]),
            [self.customer]
        )

    def test_index_context_has_empty_cart(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.context["cart_items"], [])
        self.assertEqual(response.context["cart_total"], 0)

    def test_index_context_has_selected_customer(self):
        session = self.client.session
        session["selected_customer_id"] = self.customer.id
        session.save()

        response = self.client.get(reverse("index"))

        self.assertEqual(
            response.context["selected_customer"],
            self.customer
        )

    def test_index_calculates_cart_total(self):
        session = self.client.session
        session["cart"] = [self.book.id, self.book.id]
        session.save()

        response = self.client.get(reverse("index"))

        self.assertEqual(response.context["cart_total"], 1480)
        self.assertEqual(len(response.context["cart_items"]), 2)

    def test_index_calculates_discount(self):
        product = Product.objects.create(name="Товар", price=5000)

        session = self.client.session
        session["cart"] = [product.id]
        session.save()

        response = self.client.get(reverse("index"))

        self.assertEqual(response.context["discount_percent"], 3)
        self.assertEqual(response.context["discount_amount"], 150)
        self.assertEqual(response.context["final_total"], 4850)


class DiscountTestCase(TestCase):
    def test_discount_zero_below_5000(self):
        self.assertEqual(calculate_discount(4999), 0)

    def test_discount_three_percent_from_5000(self):
        self.assertEqual(calculate_discount(5000), 3)

    def test_discount_five_percent_from_10000(self):
        self.assertEqual(calculate_discount(10000), 5)

    def test_discount_ten_percent_from_20000(self):
        self.assertEqual(calculate_discount(20000), 10)

    def test_discount_boundary_values(self):
        values = [
            (0, 0),
            (4999, 0),
            (5000, 3),
            (9999, 3),
            (10000, 5),
            (19999, 5),
            (20000, 10),
        ]

        for total, expected in values:
            with self.subTest(total=total):
                self.assertEqual(calculate_discount(total), expected)


class CartViewTestCase(TestCase):
    def setUp(self):
        self.book = Product.objects.create(name="Книга", price=740)
        self.pen = Product.objects.create(name="Ручка", price=50)

    def test_add_product_to_cart(self):
        response = self.client.post(
            reverse("add_to_cart", args=[self.book.id])
        )

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(self.client.session["cart"], [self.book.id])

    def test_add_multiple_products_to_cart(self):
        self.client.post(reverse("add_to_cart", args=[self.book.id]))
        self.client.post(reverse("add_to_cart", args=[self.pen.id]))

        self.assertEqual(
            self.client.session["cart"],
            [self.book.id, self.pen.id]
        )

    def test_add_same_product_twice(self):
        self.client.post(reverse("add_to_cart", args=[self.book.id]))
        self.client.post(reverse("add_to_cart", args=[self.book.id]))

        self.assertEqual(
            self.client.session["cart"],
            [self.book.id, self.book.id]
        )

    def test_add_nonexistent_product(self):
        response = self.client.post(
            reverse("add_to_cart", args=[999])
        )

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(self.client.session.get("cart", []), [])

    def test_add_to_cart_requires_post(self):
        response = self.client.get(
            reverse("add_to_cart", args=[self.book.id])
        )

        self.assertEqual(response.status_code, 400)

    def test_remove_product_from_cart(self):
        session = self.client.session
        session["cart"] = [self.book.id, self.pen.id]
        session.save()

        response = self.client.post(
            reverse("remove_from_cart", args=[0])
        )

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(self.client.session["cart"], [self.pen.id])

    def test_remove_product_by_index(self):
        session = self.client.session
        session["cart"] = [
            self.book.id,
            self.pen.id,
            self.book.id
        ]
        session.save()

        self.client.post(reverse("remove_from_cart", args=[1]))

        self.assertEqual(
            self.client.session["cart"],
            [self.book.id, self.book.id]
        )

    def test_remove_invalid_index(self):
        session = self.client.session
        session["cart"] = [self.book.id]
        session.save()

        self.client.post(reverse("remove_from_cart", args=[5]))

        self.assertEqual(self.client.session["cart"], [self.book.id])

    def test_remove_from_cart_requires_post(self):
        response = self.client.get(
            reverse("remove_from_cart", args=[0])
        )

        self.assertEqual(response.status_code, 400)


class CustomerSelectViewTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Иванов",
            address="ул. Светлая, 1"
        )

    def test_select_customer(self):
        response = self.client.post(
            reverse("select_customer"),
            {"customer": self.customer.id}
        )

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(
            self.client.session["selected_customer_id"],
            self.customer.id
        )

    def test_select_nonexistent_customer(self):
        response = self.client.post(
            reverse("select_customer"),
            {"customer": 999}
        )

        self.assertRedirects(response, reverse("index"))
        self.assertNotEqual(
            self.client.session.get("selected_customer_id"),
            999
        )

    def test_select_customer_requires_post(self):
        response = self.client.get(reverse("select_customer"))
        self.assertEqual(response.status_code, 400)


class PurchaseViewTestCase(TestCase):
    def setUp(self):
        self.book = Product.objects.create(name="Книга", price=740)
        self.pen = Product.objects.create(name="Ручка", price=50)
        self.customer = Customer.objects.create(
            name="Иванов",
            address="ул. Светлая, 1"
        )

    def set_session_data(self, cart=None, customer_id=None):
        session = self.client.session

        if cart is not None:
            session["cart"] = cart

        if customer_id is not None:
            session["selected_customer_id"] = customer_id

        session.save()

    def test_buy_page_is_available(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        response = self.client.get(reverse("buy"))

        self.assertEqual(response.status_code, 200)

    def test_buy_page_uses_correct_template(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        response = self.client.get(reverse("buy"))

        self.assertTemplateUsed(response, "shop/purchase_form.html")

    def test_buy_page_contains_customer(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        response = self.client.get(reverse("buy"))

        self.assertContains(response, "Иванов")

    def test_buy_page_contains_cart_products(self):
        self.set_session_data(
            cart=[self.book.id, self.pen.id],
            customer_id=self.customer.id
        )

        response = self.client.get(reverse("buy"))

        self.assertContains(response, "Книга")
        self.assertContains(response, "Ручка")

    def test_buy_page_requires_selected_customer(self):
        self.set_session_data(cart=[self.book.id])

        response = self.client.get(reverse("buy"))

        self.assertRedirects(response, reverse("index"))

    def test_buy_page_requires_nonempty_cart(self):
        self.set_session_data(customer_id=self.customer.id)

        response = self.client.get(reverse("buy"))

        self.assertRedirects(response, reverse("index"))

    def test_purchase_is_created_via_post(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        self.client.post(reverse("buy"))

        self.assertEqual(Purchase.objects.count(), 1)

    def test_purchase_has_correct_customer(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        self.client.post(reverse("buy"))

        purchase = Purchase.objects.first()
        self.assertEqual(purchase.customer, self.customer)

    def test_purchase_has_correct_product(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        self.client.post(reverse("buy"))

        purchase = Purchase.objects.first()
        self.assertEqual(purchase.product, self.book)

    def test_multiple_products_are_purchased(self):
        self.set_session_data(
            cart=[self.book.id, self.pen.id],
            customer_id=self.customer.id
        )

        self.client.post(reverse("buy"))

        self.assertEqual(Purchase.objects.count(), 2)

    def test_repeated_product_is_purchased_twice(self):
        self.set_session_data(
            cart=[self.book.id, self.book.id],
            customer_id=self.customer.id
        )

        self.client.post(reverse("buy"))

        self.assertEqual(Purchase.objects.count(), 2)

    def test_purchase_success_uses_correct_template(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        response = self.client.post(reverse("buy"))

        self.assertTemplateUsed(response, "shop/purchase_success.html")

    def test_purchase_success_contains_customer_name(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        response = self.client.post(reverse("buy"))

        self.assertContains(response, "Иванов")

    def test_purchase_success_contains_total(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        response = self.client.post(reverse("buy"))

        self.assertEqual(response.context["cart_total"], 740)
        self.assertEqual(response.context["final_total"], 740)

    def test_purchase_success_contains_discount(self):
        product = Product.objects.create(name="Товар", price=10000)

        self.set_session_data(
            cart=[product.id],
            customer_id=self.customer.id
        )

        response = self.client.post(reverse("buy"))

        self.assertEqual(response.context["discount_percent"], 5)
        self.assertEqual(response.context["discount_amount"], 500)
        self.assertEqual(response.context["final_total"], 9500)

    def test_cart_is_cleared_after_purchase(self):
        self.set_session_data(
            cart=[self.book.id],
            customer_id=self.customer.id
        )

        self.client.post(reverse("buy"))

        self.assertEqual(self.client.session["cart"], [])

    def test_purchase_requires_selected_customer(self):
        self.set_session_data(cart=[self.book.id])

        response = self.client.post(reverse("buy"))

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Purchase.objects.count(), 0)

    def test_purchase_requires_nonempty_cart(self):
        self.set_session_data(customer_id=self.customer.id)

        response = self.client.post(reverse("buy"))

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Purchase.objects.count(), 0)

    def test_purchase_does_not_use_customer_from_post(self):
        self.set_session_data(cart=[self.book.id])

        response = self.client.post(
            reverse("buy"),
            {"customer": self.customer.id}
        )

        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Purchase.objects.count(), 0)


class CustomerCreateViewTestCase(TestCase):
    def test_customer_add_page_is_available(self):
        response = self.client.get(reverse("customer_add"))
        self.assertEqual(response.status_code, 200)

    def test_customer_is_created_via_post(self):
        response = self.client.post(
            reverse("customer_add"),
            {
                "name": "Сидоров",
                "address": "ул. Полевая, 3"
            }
        )

        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.first().name, "Сидоров")

    def test_customer_add_redirects_to_index(self):
        response = self.client.post(
            reverse("customer_add"),
            {
                "name": "Тест",
                "address": "ул. Тестовая"
            }
        )

        self.assertRedirects(response, reverse("index"))

    def test_new_customer_is_selected_automatically(self):
        self.client.post(
            reverse("customer_add"),
            {
                "name": "Сидоров",
                "address": "ул. Полевая, 3"
            }
        )

        customer = Customer.objects.get(name="Сидоров")

        self.assertEqual(
            self.client.session["selected_customer_id"],
            customer.id
        )
