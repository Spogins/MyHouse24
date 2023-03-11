from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from account.forms import *


# Create your views here.
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


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


def get_user_role(request):
    if is_ajax(request):
        user = Profile.objects.get(pk=request.POST.get('pk'))
        return HttpResponse(user.role)


class OwnerCabinet:

    def __init__(self, request):
        """
        Initialize the OwnerCabinet.
        """
        self.session = request.session
        users = self.session.get(settings.USERS_SESSION_ID)

        if not users:
            # save an empty cart in the session
            users = self.session[settings.USERS_SESSION_ID] = {}
        self.users = users

    def set_admin(self, admin):
        self.users['admin'] = admin
        self.save()

    def set_owner(self, owner):
        self.users['owner'] = owner
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def clear(self):
        # remove cart from session
        del self.session[settings.USERS_SESSION_ID]
        self.save()

    def login_owner(self, request):
        owner = User.objects.get(id=self.session[settings.USERS_SESSION_ID]['owner'])
        login(request, owner, backend='django.contrib.auth.backends.ModelBackend')

    def login_admin(self, request):
        admin = User.objects.get(id=self.session[settings.USERS_SESSION_ID]['admin'])
        login(request, admin, backend='django.contrib.auth.backends.ModelBackend')


def has_access(permission_page):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('account:login')
            if request.session.get(settings.USERS_SESSION_ID):
                owner_cabinet = OwnerCabinet(request)
                owner_cabinet.login_admin(request)
                # owner_cabinet.clear()
            user = User.objects.get(id=request.user.id)
            try:
                if PermissionAccess.objects.filter(role=user.profile.role, page__name=permission_page, access=True).exists():
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponse('Доступ запрещен')
            except Profile.DoesNotExist:
                return HttpResponse('Доступ запрещен')
        return wrapper
    return decorator


def has_access_for_class(permission_page, user):
    return PermissionAccess.objects.filter(role=user.profile.role, page__name=permission_page, access=True).exists()