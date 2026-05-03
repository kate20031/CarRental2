from rest_framework import generics, permissions

from .models import Car
from .serializers import CarSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff


class CarListCreateAPIView(generics.ListCreateAPIView):
    queryset = Car.objects.all().order_by("-id")
    serializer_class = CarSerializer
    permission_classes = [IsAdminOrReadOnly]


class CarDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAdminOrReadOnly]