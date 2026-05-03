from rest_framework import serializers
from .models import Order, DamageInvoice


class OrderSerializer(serializers.ModelSerializer):
    car_brand = serializers.CharField(source="car.brand", read_only=True)
    car_model = serializers.CharField(source="car.model", read_only=True)
    car_plate_number = serializers.CharField(source="car.plate_number", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = [
            "user",
            "client_full_name",
            "passport_data",
            "total_amount",
            "order_status",
            "payment_status",
            "rejection_reason",
            "created_at",
        ]


class DamageInvoiceSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)
    username = serializers.CharField(source="order.user.username", read_only=True)
    car_brand = serializers.CharField(source="order.car.brand", read_only=True)
    car_model = serializers.CharField(source="order.car.model", read_only=True)

    class Meta:
        model = DamageInvoice
        fields = "__all__"