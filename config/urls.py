from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.urls import path, include
from orders.views import payment_page
from cars.views import cars_page, car_create_page, car_edit_page, car_delete
from cars.views import cars_page
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import login_view, register_view, logout_view
from orders.views import (
    order_create_page,
    my_orders,
    order_details,
    pay_order,
    admin_orders,
    approve_order,
    reject_order,
    returns_page, return_order
)


def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("/orders/")
        return redirect("/cars/")
    return redirect("/login/")


urlpatterns = [
    path("", home),

    path("cars/", cars_page, name="cars"),
    path("cars/create/", car_create_page, name="car_create"),
    path("cars/edit/<int:car_id>/", car_edit_page, name="car_edit"),
    path("cars/delete/<int:car_id>/", car_delete, name="car_delete"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),

    path("admin/", admin.site.urls),
    path("orders/payment/<int:order_id>/", payment_page, name="payment_page"),
    # USER
    path("orders/create/", order_create_page),
    path("orders/my/", my_orders),
    path("orders/details/<int:order_id>/", order_details),
    path("orders/pay/<int:order_id>/", pay_order),

    # ADMIN
    path("orders/", admin_orders),
    path("orders/approve/<int:order_id>/", approve_order),
    path("orders/reject/<int:order_id>/", reject_order),

    path("returns/", returns_page, name="returns"),
    path("returns/<int:order_id>/", return_order, name="return_order"),

    path("api/cars/", include("cars.api_urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/orders/", include("orders.api_urls")),
]