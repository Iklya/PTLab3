from django.test import TestCase
from django.urls import reverse

from shop.models import Customer, Product, Purchase


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.book = Product.objects.create(name="Книга", price=740)
        self.customer = Customer.objects.create(
            name="Иванов",
            address="ул. Светлая, 1"
        )

    def test_index_returns_200(self):
        """Главная страница доступна."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        """Главная использует шаблон shop/index.html."""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'shop/index.html')

    def test_index_contains_product_name(self):
        """На главной отображается товар."""
        response = self.client.get('/')
        self.assertContains(response, "Книга")

    def test_index_contains_customer_name(self):
        """На главной отображается покупатель."""
        response = self.client.get('/')
        self.assertContains(response, "Иванов")

    def test_index_context_has_products(self):
        """В контексте есть products."""
        response = self.client.get('/')
        self.assertIn('products', response.context)
        self.assertEqual(list(response.context['products']), [self.book])

    def test_index_context_has_customers(self):
        """В контексте есть customers."""
        response = self.client.get('/')
        self.assertIn('customers', response.context)
        self.assertEqual(list(response.context['customers']), [self.customer])


class PurchaseCreateViewTestCase(TestCase):
    def setUp(self):
        self.book = Product.objects.create(name="Книга", price=740)
        self.pen = Product.objects.create(name="Ручка", price=50)
        self.customer = Customer.objects.create(
            name="Иванов",
            address="ул. Светлая, 1"
        )

    def test_buy_page_is_available(self):
        """Страница покупки доступна."""
        response = self.client.get('/buy/')
        self.assertEqual(response.status_code, 200)

    def test_buy_page_uses_correct_template(self):
        """Страница покупки использует шаблон purchase_form."""
        response = self.client.get('/buy/')
        self.assertTemplateUsed(response, 'shop/purchase_form.html')

    def test_purchase_is_created_via_post(self):
        """POST создаёт покупку."""
        self.client.post('/buy/', {
            'customer': self.customer.id,
            'product': self.book.id
        })
        self.assertEqual(Purchase.objects.count(), 1)

    def test_purchase_has_correct_customer(self):
        """Покупка привязана к выбранному покупателю."""
        self.client.post('/buy/', {
            'customer': self.customer.id,
            'product': self.book.id
        })
        purchase = Purchase.objects.first()
        self.assertEqual(purchase.customer, self.customer)

    def test_purchase_has_correct_product(self):
        """Покупка привязана к выбранному товару."""
        self.client.post('/buy/', {
            'customer': self.customer.id,
            'product': self.book.id
        })
        purchase = Purchase.objects.first()
        self.assertEqual(purchase.product, self.book)

    def test_response_contains_customer_name(self):
        """Ответ содержит имя покупателя."""
        response = self.client.post('/buy/', {
            'customer': self.customer.id,
            'product': self.book.id
        })
        self.assertContains(response, "Иванов")

    def test_response_contains_total_spent(self):
        """Ответ содержит сумму покупок."""
        response = self.client.post('/buy/', {
            'customer': self.customer.id,
            'product': self.book.id
        })
        self.assertContains(response, "740")

    def test_response_contains_discount_percent(self):
        """Ответ содержит процент скидки."""
        response = self.client.post('/buy/', {
            'customer': self.customer.id,
            'product': self.book.id
        })
        self.assertContains(response, "0")

    def test_response_contains_total_with_discount(self):
        """Ответ содержит итог к оплате."""
        response = self.client.post('/buy/', {
            'customer': self.customer.id,
            'product': self.book.id
        })
        self.assertContains(response, "К оплате")

    def test_repeated_purchases_increase_total(self):
        """Повторные покупки увеличивают сумму."""
        self.client.post('/buy/', {
            'customer': self.customer.id,
            'product': self.book.id
        })
        self.client.post('/buy/', {
            'customer': self.customer.id,
            'product': self.pen.id
        })
        self.assertEqual(self.customer.total_spent(), 790)

    def test_discount_appears_after_many_purchases(self):
        """После нескольких покупок появляется скидка."""
        for _ in range(7):
            self.client.post('/buy/', {
                'customer': self.customer.id,
                'product': self.book.id
            })
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.total_spent(), 5180)
        self.assertEqual(self.customer.discount_percent(), 3)

    def test_discount_increases_on_more_purchases(self):
        """Скидка растёт при новых покупках."""
        for _ in range(14):
            self.client.post('/buy/', {
                'customer': self.customer.id,
                'product': self.book.id
            })
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.discount_percent(), 5)


class CustomerCreateViewTestCase(TestCase):
    def test_customer_add_page_is_available(self):
        """Страница добавления покупателя доступна."""
        response = self.client.get('/customer/add/')
        self.assertEqual(response.status_code, 200)

    def test_customer_is_created_via_post(self):
        """POST создаёт покупателя."""
        self.client.post('/customer/add/', {
            'name': "Сидоров",
            'address': "ул. Полевая, 3"
        })
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Customer.objects.first().name, "Сидоров")

    def test_customer_add_redirects_to_index(self):
        """После создания покупателя редирект на '/'."""
        response = self.client.post('/customer/add/', {
            'name': "Тест",
            'address': "ул. Тестовая"
        })
        self.assertRedirects(response, '/')