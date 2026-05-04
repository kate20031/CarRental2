from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from .models import Order, DamageInvoice
from cars.models import Car


from datetime import datetime, date

@login_required
def order_create_page(request):
    car_id = request.GET.get("car_id")
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        rent_start = request.POST.get("rent_start")
        rent_end = request.POST.get("rent_end")

        try:
            start_date = datetime.strptime(rent_start, "%Y-%m-%d").date()
            end_date = datetime.strptime(rent_end, "%Y-%m-%d").date()
        except:
            return render(request, "orders/create.html", {
                "car": car,
                "error": "Невірний формат дати"
            })

        today = date.today()

        # перевірка 1: дати в минулому
        if start_date < today:
            return render(request, "orders/create.html", {
                "car": car,
                "error": "Дата початку не може бути в минулому"
            })

        # перевірка 2: початок > кінець
        if start_date > end_date:
            return render(request, "orders/create.html", {
                "car": car,
                "error": "Дата початку не може бути пізніше дати завершення"
            })

        days = (end_date - start_date).days + 1
        total = days * car.price_per_day

        Order.objects.create(
            user=request.user,
            car=car,
            client_full_name=request.user.profile.full_name,
            passport_data=request.user.profile.passport_data,
            rent_start=start_date,
            rent_end=end_date,
            total_amount=total,
        )

        return redirect("/orders/my/")

    return render(request, "orders/create.html", {"car": car})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")
    return render(request, "orders/my.html", {"orders": orders})


@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/details.html", {"order": order})


@login_required
def pay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment_type = request.GET.get("type", "rent")

    if request.method == "POST":
        if payment_type == "repair":
            invoice = get_object_or_404(DamageInvoice, order=order)

            invoice.is_paid = True
            invoice.save()

            order.order_status = "returned"
            order.car.status = "available"
            order.car.save()
            order.save()

        else:
            if order.order_status == "approved" and order.payment_status == "unpaid":
                order.payment_status = "paid"
                order.order_status = "active"
                order.car.status = "rented"
                order.car.save()
                order.save()

    return redirect("/orders/my/")


@user_passes_test(lambda u: u.is_staff)
def admin_orders(request):
    return render(request, "orders/admin_list.html")

@user_passes_test(lambda u: u.is_staff)
def approve_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        if order.order_status == "pending":
            order.order_status = "approved"
            order.car.status = "reserved"
            order.car.save()
            order.save()

    return redirect("/orders/")


@user_passes_test(lambda u: u.is_staff)
def reject_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        if order.order_status == "pending":
            order.order_status = "rejected"
            order.rejection_reason = request.POST.get("rejection_reason")
            order.car.status = "available"
            order.car.save()
            order.save()

    return redirect("/orders/")

def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment_type = request.GET.get("type", "rent")

    if payment_type == "repair":
        invoice = get_object_or_404(DamageInvoice, order=order)
        amount = invoice.repair_amount
    else:
        amount = order.total_amount

    return render(request, "orders/payment.html", {
        "order": order,
        "amount": amount,
        "payment_type": payment_type,
    })



@user_passes_test(lambda u: u.is_staff)
def returns_page(request):
    return render(request, "orders/returns.html")


@user_passes_test(lambda u: u.is_staff)
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        has_damage = request.POST.get("has_damage")

        if has_damage == "yes":
            description = request.POST.get("damage_description", "").strip()
            repair_amount_raw = request.POST.get("repair_amount", "").strip()

            if not description:
                messages.error(request, "Введіть опис пошкодження")
                return redirect("/returns/")

            if not repair_amount_raw:
                messages.error(request, "Введіть суму ремонту")
                return redirect("/returns/")

            try:
                repair_amount = Decimal(repair_amount_raw)
            except InvalidOperation:
                messages.error(request, "Сума ремонту має бути числом")
                return redirect("/returns/")

            if repair_amount <= 0:
                messages.error(request, "Сума ремонту має бути більше 0")
                return redirect("/returns/")

            DamageInvoice.objects.create(
                order=order,
                description=description,
                repair_amount=repair_amount
            )

            order.order_status = "damage_pending"
            order.save()

        else:
            order.order_status = "returned"
            order.car.status = "available"
            order.car.save()
            order.save()

    return redirect("/returns/")