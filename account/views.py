from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View

from account.forms import *


# Create your views here.

class LoginView(View):

    def get(self, request, *args, **kwargs):
        context = {'form': LoginForm()}
        return render(request, 'account/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('/admin_app')
        return render(request, 'account/login.html', context)


class LoginOwnerView(View):

    def get(self, request, *args, **kwargs):
        form = LoginOwnerForm(request.POST or None)
        context = {'form': form}
        return render(request, "account/login_owner.html", context)

    def post(self, request, *args, **kwargs):
        form = LoginOwnerForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('/cabinet/index')
        return render(request, 'account/login_owner.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('/account/login_owner')