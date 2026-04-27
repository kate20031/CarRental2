from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    rental_days = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["user", "status", "total_price", "rejection_reason"]