from django.contrib.auth import logout, login
from django.http import HttpRequest
from django.shortcuts import render, redirect

from core.forms import SignUp_form
from profiles.models import Profile

# Create your views here.

def home(request):
    is_organizer = request.user.groups.filter(name='Organizer').exists()

    return render(request, 'core/index.html', {'is_organizer': is_organizer})


def register(request):
    if request.method == "POST":
        form = SignUp_form(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Profile.objects.create(user=user)

            return redirect('home')
    else:
        form = SignUp_form()
    return render(request, 'core/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')

