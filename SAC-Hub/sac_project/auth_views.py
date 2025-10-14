from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from users.models import User, Role

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("student-dashboard")
        else:
            return render(request, "login.html", {"form": {}, "error": True})
    return render(request, "login.html", {"form": {}})

def logout_view(request):
    logout(request)
    return redirect("login")
