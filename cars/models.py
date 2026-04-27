from django.db import models


class Car(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("rented", "Rented"),
        ("maintenance", "Maintenance"),
    ]

    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    manufacture_year = models.IntegerField()
    plate_number = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.model}"