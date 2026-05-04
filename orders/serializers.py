from rest_framework import serializers
from .models import Order, DamageInvoice


class DamageInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamageInvoice
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    car_brand = serializers.CharField(source="car.brand", read_only=True)
    car_model = serializers.CharField(source="car.model", read_only=True)
    car_plate_number = serializers.CharField(source="car.plate_number", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    invoice = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"

    def get_invoice(self, obj):
        try:
            invoice = DamageInvoice.objects.get(order=obj)
            return DamageInvoiceSerializer(invoice).data
        except DamageInvoice.DoesNotExist:
            return None