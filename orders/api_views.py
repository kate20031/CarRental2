from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from cars.models import Car
from .models import Order, DamageInvoice
from .serializers import OrderSerializer, DamageInvoiceSerializer

import logging

logger = logging.getLogger(__name__)

@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def orders_api(request):
    """
    GET:
    - admin бачить всі замовлення
    - client бачить тільки свої

    POST:
    - client створює нове замовлення
    """

    if request.method == "GET":
        if request.user.is_staff:
            orders = Order.objects.all().order_by("-id")
        else:
            orders = Order.objects.filter(user=request.user).order_by("-id")

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        car_id = request.data.get("car_id")
        rent_start = request.data.get("rent_start")
        rent_end = request.data.get("rent_end")

        if not car_id or not rent_start or not rent_end:
            return Response(
                {"error": "car_id, rent_start і rent_end обов'язкові"},
                status=status.HTTP_400_BAD_REQUEST
            )

        car = get_object_or_404(Car, id=car_id)

        if car.status != "available":
            return Response(
                {"error": "Автомобіль недоступний для оренди"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = datetime.strptime(rent_start, "%Y-%m-%d").date()
            end_date = datetime.strptime(rent_end, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Невірний формат дати. Використовуйте YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date < date.today():
            return Response(
                {"error": "Дата початку не може бути в минулому"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date > end_date:
            return Response(
                {"error": "Дата початку не може бути пізніше дати завершення"},
                status=status.HTTP_400_BAD_REQUEST
            )

        days = (end_date - start_date).days + 1
        total = days * car.price_per_day

        profile = getattr(request.user, "profile", None)

        order = Order.objects.create(
            user=request.user,
            car=car,
            client_full_name=profile.full_name if profile else request.user.username,
            passport_data=profile.passport_data if profile else "Unknown",
            rent_start=start_date,
            rent_end=end_date,
            total_amount=total,
        )

        logger.info(
            f"Order {order.id} created by user {request.user.username} "
            f"for car {car.id} from {start_date} to {end_date}"
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_orders_api(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def approve_order_api(request, order_id):
    if not request.user.is_staff:
        return Response(
            {"error": "Доступ заборонено"},
            status=status.HTTP_403_FORBIDDEN
        )

    order = get_object_or_404(Order, id=order_id)

    if order.order_status != "pending":
        return Response(
            {"error": "Можна підтвердити тільки pending замовлення"},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.order_status = "approved"
    order.car.status = "reserved"
    order.car.save()
    order.save()

    logger.info(
        f"Order {order.id} approved by admin {request.user.username}"
    )

    return Response(OrderSerializer(order).data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reject_order_api(request, order_id):
    if not request.user.is_staff:
        return Response(
            {"error": "Доступ заборонено"},
            status=status.HTTP_403_FORBIDDEN
        )

    order = get_object_or_404(Order, id=order_id)
    reason = request.data.get("rejection_reason", "").strip()

    if order.order_status != "pending":
        return Response(
            {"error": "Можна відхилити тільки pending замовлення"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not reason:
        return Response(
            {"error": "Вкажіть причину відмови"},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.order_status = "rejected"
    order.rejection_reason = reason
    order.car.status = "available"
    order.car.save()
    order.save()

    logger.warning(
        f"Order {order.id} rejected by admin {request.user.username}. "
        f"Reason: {reason}"
    )

    return Response(OrderSerializer(order).data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def pay_order_api(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment_type = request.data.get("payment_type", "rent")

    if payment_type == "rent":
        if order.order_status != "approved":
            return Response(
                {"error": "Оренду можна оплатити тільки після підтвердження адміном"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.payment_status == "paid":
            return Response(
                {"error": "Оренда вже оплачена"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.payment_status = "paid"
        order.order_status = "active"
        order.car.status = "rented"
        order.car.save()
        order.save()

        logger.info(
            f"Rent payment completed for order {order.id} "
            f"by user {request.user.username}"
        )

        return Response({
            "message": "Оренду оплачено",
            "order": OrderSerializer(order).data
        })

    if payment_type == "repair":
        invoice = get_object_or_404(DamageInvoice, order=order)

        if invoice.is_paid:
            return Response(
                {"error": "Ремонт вже оплачено"},
                status=status.HTTP_400_BAD_REQUEST
            )

        invoice.is_paid = True
        invoice.save()

        order.order_status = "returned"
        order.car.status = "available"
        order.car.save()
        order.save()

        logger.info(
            f"Repair payment completed for order {order.id} "
            f"by user {request.user.username}"
        )

        return Response({
            "message": "Ремонт оплачено",
            "order": OrderSerializer(order).data,
            "invoice": DamageInvoiceSerializer(invoice).data
        })

    return Response(
        {"error": "Невідомий тип оплати"},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def returns_api(request):
    if not request.user.is_staff:
        return Response(
            {"error": "Доступ заборонено"},
            status=status.HTTP_403_FORBIDDEN
        )

    orders = Order.objects.filter(order_status="active").order_by("-id")
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def return_order_api(request, order_id):
    if not request.user.is_staff:
        return Response(
            {"error": "Доступ заборонено"},
            status=status.HTTP_403_FORBIDDEN
        )

    order = get_object_or_404(Order, id=order_id)

    if order.order_status != "active":
        return Response(
            {"error": "Повернути можна тільки active замовлення"},
            status=status.HTTP_400_BAD_REQUEST
        )

    has_damage = request.data.get("has_damage", False)

    if has_damage:
        description = request.data.get("damage_description", "").strip()
        repair_amount_raw = str(request.data.get("repair_amount", "")).strip()

        if not description:
            return Response(
                {"error": "Введіть опис пошкодження"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not repair_amount_raw:
            return Response(
                {"error": "Введіть суму ремонту"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            repair_amount = Decimal(repair_amount_raw)
        except InvalidOperation:
            return Response(
                {"error": "Сума ремонту має бути числом"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if repair_amount <= 0:
            return Response(
                {"error": "Сума ремонту має бути більше 0"},
                status=status.HTTP_400_BAD_REQUEST
            )

        invoice = DamageInvoice.objects.create(
            order=order,
            description=description,
            repair_amount=repair_amount
        )

        order.order_status = "damage_pending"
        order.save()

        logger.warning(
            f"Damage registered for order {order.id} by admin {request.user.username}. "
            f"Invoice {invoice.id}, amount {repair_amount}"
        )

        return Response({
            "message": "Повернення з пошкодженням зареєстровано",
            "order": OrderSerializer(order).data,
            "invoice": DamageInvoiceSerializer(invoice).data
        })

    order.order_status = "returned"
    order.car.status = "available"
    order.car.save()
    order.save()

    logger.info(
        f"Return without damage registered for order {order.id} "
        f"by admin {request.user.username}"
    )

    return Response({
        "message": "Повернення без пошкоджень зареєстровано",
        "order": OrderSerializer(order).data
    })