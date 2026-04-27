from django.db import models
from django.contrib.auth.models import User
from cars.models import Car


class Order(models.Model):
    ORDER_STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("active", "Active"),
        ("damage_pending", "Repair Payment Pending"),
        ("returned", "Returned"),
        ("closed", "Closed"),
    ]

    PAYMENT_STATUS = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    client_full_name = models.CharField(max_length=150)
    passport_data = models.CharField(max_length=100)

    rent_start = models.DateField()
    rent_end = models.DateField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="unpaid")

    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class DamageInvoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    description = models.TextField()
    repair_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repair invoice for order #{self.order.id}"