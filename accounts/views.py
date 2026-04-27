from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Profile


def logout_view(request):
    logout(request)
    return redirect("/login/")

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("/orders/")
        return redirect("/cars/")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect("/orders/")   # адмін
            else:
                return redirect("/cars/")     # клієнт

        return render(request, "login.html", {
            "error": "Неправильний логін або пароль"
        })

    return render(request, "login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/cars/")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        passport_data = request.POST.get("passport_data", "").strip()
        full_name = request.POST.get("full_name", "").strip()

        if User.objects.filter(username__iexact=username).exists():
            return render(request, "register.html", {
                "error": "Користувач з таким логіном вже існує"
            })

        user = User.objects.create_user(username=username, password=password)

        Profile.objects.create(
            user=user,
            full_name=full_name,
            passport_data=passport_data
        )

        login(request, user)
        return redirect("/cars/")

    return render(request, "register.html")