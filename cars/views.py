from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Car


@login_required
def cars_page(request):
    return render(request, "cars/index.html")


@user_passes_test(lambda u: u.is_staff)
def car_create_page(request):
    if request.method == "POST":
        Car.objects.create(
            brand=request.POST.get("brand"),
            model=request.POST.get("model"),
            manufacture_year=request.POST.get("manufacture_year"),
            plate_number=request.POST.get("plate_number"),
            color=request.POST.get("color"),
            price_per_day=request.POST.get("price_per_day"),
            image_url=request.POST.get("image_url"),
        )
        return redirect("/cars/")

    return render(request, "cars/create.html")


@user_passes_test(lambda u: u.is_staff)
def car_edit_page(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        car.brand = request.POST.get("brand")
        car.model = request.POST.get("model")
        car.manufacture_year = request.POST.get("manufacture_year")
        car.plate_number = request.POST.get("plate_number")
        car.color = request.POST.get("color")
        car.price_per_day = request.POST.get("price_per_day")
        car.status = request.POST.get("status")
        car.image_url = request.POST.get("image_url")
        car.save()
        return redirect("/cars/")

    return render(request, "cars/edit.html", {"car": car})


@user_passes_test(lambda u: u.is_staff)
def car_delete(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        car.delete()

    return redirect("/cars/")