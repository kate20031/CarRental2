from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from accounts.models import Profile
from cars.models import Car
from orders.models import Order, DamageInvoice


class OrdersApiWorkflowTests(TestCase):
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

        self.second_car = Car.objects.create(
            brand="BMW",
            model="X5",
            manufacture_year=2021,
            plate_number="KA5678BM",
            color="Black",
            price_per_day=Decimal("1800.00"),
            status="available",
        )

        self.start_date = date.today() + timedelta(days=3)
        self.end_date = date.today() + timedelta(days=5)

    def create_order_as_user(self, car=None):
        if car is None:
            car = self.car

        self.client.force_authenticate(user=self.user)

        response = self.client.post("/api/orders/", {
            "car_id": car.id,
            "rent_start": self.start_date.isoformat(),
            "rent_end": self.end_date.isoformat(),
        }, format="json")

        self.assertEqual(response.status_code, 201)
        return Order.objects.get(id=response.data["id"])

    def approve_order_as_admin(self, order):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(f"/api/orders/{order.id}/approve/")

        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        order.car.refresh_from_db()

        self.assertEqual(order.order_status, "approved")
        self.assertEqual(order.car.status, "reserved")

    def pay_rent_as_user(self, order):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f"/api/orders/{order.id}/pay/", {
            "payment_type": "rent"
        }, format="json")

        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        order.car.refresh_from_db()

        self.assertEqual(order.payment_status, "paid")
        self.assertEqual(order.order_status, "active")
        self.assertEqual(order.car.status, "rented")

    def test_user_can_create_order_with_correct_total_amount(self):
        order = self.create_order_as_user()

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.car, self.car)
        self.assertEqual(order.order_status, "pending")
        self.assertEqual(order.payment_status, "unpaid")
        self.assertEqual(order.client_full_name, "Client Test")
        self.assertEqual(order.passport_data, "AB123456")

        # 3 дні: today+3, today+4, today+5
        self.assertEqual(order.total_amount, Decimal("3600.00"))

    def test_user_cannot_create_order_with_past_date(self):
        self.client.force_authenticate(user=self.user)

        yesterday = date.today() - timedelta(days=1)

        response = self.client.post("/api/orders/", {
            "car_id": self.car.id,
            "rent_start": yesterday.isoformat(),
            "rent_end": self.end_date.isoformat(),
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Дата початку не може бути в минулому", response.data["error"])

    def test_user_cannot_create_order_with_invalid_date_range(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post("/api/orders/", {
            "car_id": self.car.id,
            "rent_start": self.end_date.isoformat(),
            "rent_end": self.start_date.isoformat(),
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Дата початку не може бути пізніше", response.data["error"])

    def test_user_cannot_create_order_for_unavailable_car(self):
        self.car.status = "rented"
        self.car.save()

        self.client.force_authenticate(user=self.user)

        response = self.client.post("/api/orders/", {
            "car_id": self.car.id,
            "rent_start": self.start_date.isoformat(),
            "rent_end": self.end_date.isoformat(),
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Автомобіль недоступний", response.data["error"])

    def test_admin_can_approve_order(self):
        order = self.create_order_as_user()

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f"/api/orders/{order.id}/approve/")

        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        self.car.refresh_from_db()

        self.assertEqual(order.order_status, "approved")
        self.assertEqual(self.car.status, "reserved")

    def test_regular_user_cannot_approve_order(self):
        order = self.create_order_as_user()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/api/orders/{order.id}/approve/")

        self.assertEqual(response.status_code, 403)

        order.refresh_from_db()
        self.assertEqual(order.order_status, "pending")

    def test_admin_can_reject_order_with_reason(self):
        order = self.create_order_as_user()

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(f"/api/orders/{order.id}/reject/", {
            "rejection_reason": "Incorrect dates"
        }, format="json")

        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        order.car.refresh_from_db()

        self.assertEqual(order.order_status, "rejected")
        self.assertEqual(order.rejection_reason, "Incorrect dates")
        self.assertEqual(order.car.status, "available")

    def test_admin_cannot_reject_order_without_reason(self):
        order = self.create_order_as_user()

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(f"/api/orders/{order.id}/reject/", {
            "rejection_reason": ""
        }, format="json")

        self.assertEqual(response.status_code, 400)

        order.refresh_from_db()
        self.assertEqual(order.order_status, "pending")

    def test_user_can_pay_only_approved_order(self):
        order = self.create_order_as_user()

        self.client.force_authenticate(user=self.user)

        response = self.client.post(f"/api/orders/{order.id}/pay/", {
            "payment_type": "rent"
        }, format="json")

        self.assertEqual(response.status_code, 400)

        order.refresh_from_db()
        self.assertEqual(order.payment_status, "unpaid")
        self.assertEqual(order.order_status, "pending")

    def test_full_rent_payment_flow(self):
        order = self.create_order_as_user()

        self.approve_order_as_admin(order)
        self.pay_rent_as_user(order)

        order.refresh_from_db()
        self.assertEqual(order.order_status, "active")
        self.assertEqual(order.payment_status, "paid")
        self.assertEqual(order.car.status, "rented")

    def test_admin_can_register_return_without_damage(self):
        order = self.create_order_as_user()
        self.approve_order_as_admin(order)
        self.pay_rent_as_user(order)

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(f"/api/orders/returns/{order.id}/", {
            "has_damage": False
        }, format="json")

        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        order.car.refresh_from_db()

        self.assertEqual(order.order_status, "returned")
        self.assertEqual(order.car.status, "available")
        self.assertFalse(DamageInvoice.objects.filter(order=order).exists())

    def test_admin_can_register_return_with_damage_and_invoice(self):
        order = self.create_order_as_user()
        self.approve_order_as_admin(order)
        self.pay_rent_as_user(order)

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(f"/api/orders/returns/{order.id}/", {
            "has_damage": True,
            "damage_description": "Broken headlights",
            "repair_amount": "700.00",
        }, format="json")

        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()

        self.assertEqual(order.order_status, "damage_pending")
        self.assertTrue(DamageInvoice.objects.filter(order=order).exists())

        invoice = DamageInvoice.objects.get(order=order)
        self.assertEqual(invoice.description, "Broken headlights")
        self.assertEqual(invoice.repair_amount, Decimal("700.00"))
        self.assertFalse(invoice.is_paid)

    def test_customer_can_pay_repair_invoice_after_damage(self):
        order = self.create_order_as_user()
        self.approve_order_as_admin(order)
        self.pay_rent_as_user(order)

        self.client.force_authenticate(user=self.admin)

        self.client.post(f"/api/orders/returns/{order.id}/", {
            "has_damage": True,
            "damage_description": "Broken headlights",
            "repair_amount": "700.00",
        }, format="json")

        self.client.force_authenticate(user=self.user)

        response = self.client.post(f"/api/orders/{order.id}/pay/", {
            "payment_type": "repair"
        }, format="json")

        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        order.car.refresh_from_db()

        invoice = DamageInvoice.objects.get(order=order)

        self.assertTrue(invoice.is_paid)
        self.assertEqual(order.order_status, "returned")
        self.assertEqual(order.car.status, "available")

    def test_admin_can_see_all_orders_but_user_only_own_orders(self):
        order1 = self.create_order_as_user(car=self.car)

        another_user = User.objects.create_user(
            username="another_client",
            password="client12345"
        )

        Profile.objects.create(
            user=another_user,
            full_name="Another Client",
            passport_data="CD987654"
        )

        order2 = Order.objects.create(
            user=another_user,
            car=self.second_car,
            client_full_name="Another Client",
            passport_data="CD987654",
            rent_start=self.start_date,
            rent_end=self.end_date,
            total_amount=Decimal("5400.00"),
        )

        self.client.force_authenticate(user=self.user)
        user_response = self.client.get("/api/orders/")

        self.assertEqual(user_response.status_code, 200)
        self.assertEqual(len(user_response.data), 1)
        self.assertEqual(user_response.data[0]["id"], order1.id)

        self.client.force_authenticate(user=self.admin)
        admin_response = self.client.get("/api/orders/")

        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(len(admin_response.data), 2)

        ids = [order["id"] for order in admin_response.data]
        self.assertIn(order1.id, ids)
        self.assertIn(order2.id, ids)