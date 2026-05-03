from django.urls import path
from .api_views import CarListCreateAPIView, CarDetailAPIView

urlpatterns = [
    path("", CarListCreateAPIView.as_view(), name="api_cars"),
    path("<int:pk>/", CarDetailAPIView.as_view(), name="api_car_detail"),
]