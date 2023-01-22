from django.shortcuts import render
from django.views import View


# Create your views here.

class LoginView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'account/login.html', context)

    def post(self, request, *args, **kwargs):
        context = {}
        return render(request, 'account/login.html', context)


class LoginOwnerView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'account/login_owner.html', context)

    def post(self, request, *args, **kwargs):
        context = {}
        return render(request, 'account/login_owner.html', context)