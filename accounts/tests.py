from django.test import TestCase, Client
from django.contrib.auth.models import User

from accounts.models import Profile


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_creates_user_and_profile(self):
        response = self.client.post("/register/", {
            "username": "client_test",
            "password": "client12345",
            "full_name": "Client Test",
            "passport_data": "AB123456",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="client_test").exists())

        user = User.objects.get(username="client_test")
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.full_name, "Client Test")
        self.assertEqual(user.profile.passport_data, "AB123456")
        self.assertFalse(user.is_staff)

    def test_register_duplicate_username_returns_error(self):
        User.objects.create_user(username="client_test", password="client12345")

        response = self.client.post("/register/", {
            "username": "client_test",
            "password": "anotherpass",
            "full_name": "Another Client",
            "passport_data": "CD987654",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Користувач з таким логіном вже існує")
        self.assertEqual(User.objects.filter(username="client_test").count(), 1)

    def test_login_client_redirects_to_cars(self):
        User.objects.create_user(username="client_test", password="client12345")

        response = self.client.post("/login/", {
            "username": "client_test",
            "password": "client12345",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/cars/")

    def test_login_admin_redirects_to_orders(self):
        User.objects.create_superuser(
            username="admin_test",
            email="admin@test.com",
            password="admin12345"
        )

        response = self.client.post("/login/", {
            "username": "admin_test",
            "password": "admin12345",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/orders/")

    def test_wrong_login_shows_error(self):
        response = self.client.post("/login/", {
            "username": "wrong",
            "password": "wrong",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неправильний логін або пароль")

    def test_jwt_token_obtain_pair_success(self):
        User.objects.create_user(username="api_user", password="api12345")

        response = self.client.post(
            "/api/token/",
            data={
                "username": "api_user",
                "password": "api12345",
            },
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_jwt_token_wrong_credentials_fails(self):
        User.objects.create_user(username="api_user", password="api12345")

        response = self.client.post(
            "/api/token/",
            data={
                "username": "api_user",
                "password": "wrongpass",
            },
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)