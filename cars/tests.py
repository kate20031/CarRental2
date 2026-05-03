from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from accounts.models import Profile
from cars.models import Car


class CarsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_superuser(
            username="admin_test",
            email="admin@test.com",
            password="admin12345"
        )

        self.user = User.objects.create_user(
            username="client_test",
            password="client12345"
        )

        Profile.objects.create(
            user=self.user,
            full_name="Client Test",
            passport_data="AB123456"
        )

        self.car = Car.objects.create(
            brand="Toyota",
            model="Corolla",
            manufacture_year=2020,
            plate_number="AA1234BC",
            color="White",
            price_per_day=Decimal("1200.00"),
            status="available",
        )

    def test_anonymous_user_cannot_access_cars_api(self):
        response = self.client.get("/api/cars/")
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_see_cars(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/cars/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["brand"], "Toyota")
        self.assertEqual(response.data[0]["model"], "Corolla")

    def test_regular_user_cannot_create_car(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/api/cars/", {
            "brand": "BMW",
            "model": "X5",
            "manufacture_year": 2021,
            "plate_number": "KA5678BM",
            "color": "Black",
            "price_per_day": "1800.00",
            "status": "available",
        }, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Car.objects.filter(brand="BMW").exists())

    def test_admin_can_create_car(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post("/api/cars/", {
            "brand": "BMW",
            "model": "X5",
            "manufacture_year": 2021,
            "plate_number": "KA5678BM",
            "color": "Black",
            "price_per_day": "1800.00",
            "status": "available",
        }, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Car.objects.filter(brand="BMW", model="X5").exists())

    def test_admin_can_update_car_status(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/cars/{self.car.id}/",
            {"status": "maintenance"},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.car.refresh_from_db()
        self.assertEqual(self.car.status, "maintenance")

    def test_admin_can_delete_car(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(f"/api/cars/{self.car.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Car.objects.filter(id=self.car.id).exists())

    def test_regular_user_cannot_delete_car(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f"/api/cars/{self.car.id}/")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Car.objects.filter(id=self.car.id).exists())