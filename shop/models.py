
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def total_spent(self):
        """Историческая сумма всех покупок покупателя."""
        return sum(
            purchase.product.price
            for purchase in self.purchases.select_related("product").all()
        )


class Purchase(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="purchases"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name}: {self.product.name}"
