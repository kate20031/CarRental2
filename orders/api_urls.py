from django.urls import path
from . import api_views

urlpatterns = [
    path("", api_views.orders_api, name="api_orders"),
    path("my/", api_views.my_orders_api, name="api_my_orders"),

    path("<int:order_id>/approve/", api_views.approve_order_api, name="api_approve_order"),
    path("<int:order_id>/reject/", api_views.reject_order_api, name="api_reject_order"),
    path("<int:order_id>/pay/", api_views.pay_order_api, name="api_pay_order"),

    path("returns/", api_views.returns_api, name="api_returns"),
    path("returns/<int:order_id>/", api_views.return_order_api, name="api_return_order"),
]