from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.base import TemplateResponseMixin, TemplateView
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin

from account.forms import UserChangeForm, ProfileChangeForm
from account.models import Profile
from admin_app.forms import *
from admin_app.models import *


# Create your views here.
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def index(request):
    user = User.objects.get(id=request.user.id)
    return render(request, 'admin_app/statistic.html')


class CreateService(CreateView):
    template_name = 'admin_app/settings/services.html'

    def get_context_data(self, **kwargs):
        context = {
            'formset': ServiceFormset(queryset=Service.objects.all(), prefix='service'),
            'unit_formset': UnitFormset(queryset=Unit.objects.all())
        }
        return context

    def post(self, request, *args, **kwargs):
        formset = ServiceFormset(request.POST or None, queryset=Service.objects.all(), prefix='service')
        unit_formset = UnitFormset(request.POST or None, queryset=Unit.objects.all())
        if unit_formset.is_valid() and formset.is_valid:
            return self.form_valid(formset, unit_formset)

    def form_valid(self, formset, unit_formset):
        unit_formset.save()
        for form in formset:
            form.save()
        return redirect('/admin_app/services/')


@require_POST
def delete_service(request):
    pk = request.POST.get('pk')
    Service.objects.get(pk=pk).delete()
    return JsonResponse({'pk': pk})


@require_POST
def delete_unit(request):
    pk = request.POST.get('pk')
    Unit.objects.get(pk=pk).delete()
    return JsonResponse({'pk': pk})


class TariffList(ListView):
    model = Tariff
    template_name = 'admin_app/settings/tariff/index.html'


class CreateTariff(CreateView):
    model = Tariff
    form_class = TariffCreateForm
    template_name = 'admin_app/settings/tariff/create.html'
    context_object_name = 'form'
    success_url = '/admin_app/tariff_list/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = TariffServiceFormSet(queryset=TariffService.objects.none(), prefix='tariffservice_set')
        return context

    def post(self, request, *args, **kwargs):
        formset = TariffServiceFormSet(request.POST or None, prefix='tariffservice_set')
        form = TariffCreateForm(request.POST)
        if form.is_valid():
            return self.form_valid(formset, form)

    def form_valid(self, formset, form):
        tariff = form.save()
        for form in formset:
            if form.is_valid():
                if form.cleaned_data:
                    full_form = form.save()
                    full_form.tariff = tariff
                    full_form.unit = full_form.service.unit
                    full_form.save()
        return redirect('/admin_app/tariff_list/')


class UpdateTariff(UpdateView):
    model = Tariff
    template_name = 'admin_app/settings/tariff/create.html'
    success_url = '/admin_app/tariff_list/'

    def get_context_data(self, **kwargs):
        context = {
            'form': TariffCreateForm(instance=Tariff.objects.get(id=self.kwargs['pk'])),
            'formset': TariffServiceFormSet(queryset=TariffService.objects.filter(tariff=self.kwargs['pk']), prefix='tariffservice_set'),
            'name': Tariff.objects.get(id=self.kwargs['pk']).name,
            'id': self.kwargs['pk']
        }
        return context

    def post(self, request, *args, **kwargs):
        formset = TariffServiceFormSet(request.POST, prefix='tariffservice_set')
        form = TariffCreateForm(request.POST, instance=Tariff.objects.get(id=self.kwargs['pk']))
        if form.is_valid():
            return self.form_valid(formset, form)

    def form_valid(self, formset, form):
        tariff = form.save()
        for form in formset:
            if form.is_valid():
                if form.cleaned_data:
                    full_form = form.save()
                    full_form.tariff = tariff
                    full_form.unit = full_form.service.unit
                    full_form.save()
        return redirect('/admin_app/tariff_list/')


def get_unit_by_service(request):
    if is_ajax(request):
        unit = Service.objects.get(id=request.GET.get('id')).unit_id
        return HttpResponse(unit)


def get_service_by_unit(request):
    if is_ajax(request):
        service = Service.objects.get(unit=request.GET.get('id')).id
        return HttpResponse(service)


def delete_tariff(request, tariff_id):
    Tariff.objects.get(id=tariff_id).delete()
    return redirect('/admin_app/tariff_list/')


def delete_service_tariff(request):
    pk = request.POST.get('pk')
    TariffService.objects.get(pk=pk).delete()
    return JsonResponse({'pk': pk})


class ShowTariff(DetailView):
    model = Tariff
    template_name = 'admin_app/settings/tariff/tariff.html'
    context_object_name = 'tariff'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = TariffService.objects.filter(tariff=self.kwargs['pk'])
        return context


class RoleList(ListView):
    model = Role
    template_name = 'admin_app/settings/roles.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            'forms': RoleFormSet(queryset=Role.objects.all())
        }
        return context

    def post(self, request, *args, **kwargs):
        forms = RoleFormSet(request.POST)
        for form in forms:
            form.save()
        return redirect('/admin_app/roles/')


class UserList(ListView):
    model = User
    template_name = 'admin_app/settings/user/index.html'


class CreateUser(CreateView):
    model = Profile
    template_name = 'admin_app/settings/user/update.html'
    user = User()
    profile = Profile()

    def get_context_data(self, **kwargs):
        context = {
            'profile_form': ProfileChangeForm(instance=self.profile),
            'register_form': UserChangeForm(instance=self.user)
        }
        return context

    def post(self, request, *args, **kwargs):
        form_user = UserChangeForm(request.POST, instance=self.user)
        form_profile = ProfileChangeForm(request.POST, instance=self.profile)
        if form_user.is_valid() and form_profile.is_valid():
            return self.form_valid(form_user, form_profile)

    def form_valid(self, form_user, form_profile):
        created_user = form_user.save(commit=False)
        created_user.username = form_user.cleaned_data['email']
        created_user.set_password(form_user.cleaned_data['password'])
        created_user.save()

        created_profile = form_profile.save(commit=False)
        created_profile.user_id = created_user.id
        created_profile.save()
        return redirect('/admin_app/user_list/')


class UpdateUser(UpdateView):
    model = Profile
    template_name = 'admin_app/settings/user/update.html'

    def get_context_data(self, **kwargs):

        profile = Profile.objects.get(id=self.kwargs['pk'])
        context = {
            'profile_form': ProfileChangeForm(instance=profile),
            'register_form': UserChangeForm(instance=profile.user)
        }
        if kwargs.get('form'):
            context = kwargs.get('form')
        return context

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get(id=self.kwargs['pk'])
        form_user = UserChangeForm(request.POST, instance=profile.user)
        form_profile = ProfileChangeForm(request.POST, instance=profile)
        if form_user.is_valid() and form_profile.is_valid():
            return self.form_valid(form_user, form_profile)
        else:
            return self.form_invalid(form_user, form_profile)

    def form_valid(self, form_user, form_profile):
        created_user = form_user.save()
        created_user.username = form_user.cleaned_data['email']
        if form_user.cleaned_data['password']:
            created_user.set_password(form_user.cleaned_data['password'])
        created_user.save()
        form_profile.save()
        return redirect('/admin_app/user_list/')

    def form_invalid(self, form_user, form_profile):
        """If the form is invalid, render the invalid form."""
        context = {
            'profile_form': form_profile,
            'register_form': form_user
        }
        return self.render_to_response(context)


class ShowProfile(DetailView):
    model = User
    template_name = 'admin_app/settings/user/profile.html'
    context_object_name = 'user'


def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    profile = user.profile
    user.delete()
    profile.delete()
    return redirect('/admin_app/user_list/')


class PaymentDetailsView(DetailView):
    model = PaymentDetails
    template_name = 'admin_app/settings/payment_details.html'
    context_object_name = 'form'

    def get_object(self, queryset=None):
        return PaymentDetailsForm(instance=PaymentDetails.objects.get(id=1))

    def post(self, request, *args, **kwargs):
        form = PaymentDetailsForm(request.POST, instance=PaymentDetails.objects.get(id=1))
        if form.is_valid():
            return self.form_valid(form)

    def form_valid(self, form):
        form.save()
        return redirect('/admin_app/payment_details/')


class PaymentItemList(ListView):
    model = PaymentItems
    template_name = 'admin_app/settings/payment_item/index.html'


class PaymentItemCreate(CreateView):
    form_class = PaymentItemsForm
    template_name = 'admin_app/settings/payment_item/create.html'
    context_object_name = 'form'
    success_url = reverse_lazy('payment_items')


class PaymentItemUpdate(UpdateView):
    model = PaymentItems
    form_class = PaymentItemsForm
    template_name = 'admin_app/settings/payment_item/create.html'
    context_object_name = 'form'
    success_url = reverse_lazy('payment_items')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edit'] = True
        return context


def delete_payment(request, payment_id):
    PaymentItems.objects.get(id=payment_id).delete()
    return redirect('/admin_app/payment_items/')


class MainPageView(CreateView):
    template_name = 'admin_app/pages/main_page.html'
    instance = MainPage.objects.all()[0]
    instance_seo = instance.seo

    def get_context_data(self, **kwargs):
        formset = SlideFormSet(queryset=Slide.objects.all(), prefix='slide')
        form = MainPageForm(instance=self.instance)
        near_formset = NearBlockFormSet(queryset=NearBlock.objects.all(), prefix='near')
        seo_form = SeoCreateForm(instance=self.instance_seo, prefix='seo')
        context = {
            'formset': formset,
            'form': form,
            'near_formset': near_formset,
            'seo_form': seo_form
        }
        return context

    def post(self, request, *args, **kwargs):
        formset = SlideFormSet(request.POST, request.FILES, queryset=Slide.objects.all(), prefix='slide')
        form = MainPageForm(request.POST, instance=self.instance)
        near_formset = NearBlockFormSet(request.POST, request.FILES, queryset=NearBlock.objects.all(), prefix='near')
        seo_form = SeoCreateForm(request.POST, instance=self.instance_seo, prefix='seo')
        if form.is_valid() and seo_form.is_valid() and formset.is_valid() and near_formset.is_valid():
            return self.form_valid(form, seo_form, formset, near_formset)
        else:
            return self.form_invalid(form, seo_form, formset, near_formset)

    def form_valid(self, form, seo_form, formset, near_formset):
        print('++++++++++')
        form.save()
        seo_form.save()
        for form in formset:
            form.save()
        for n_form in near_formset:
            n_form.save()
        return redirect('/admin_app/main_page/')

    def form_invalid(self, form, seo_form, formset, near_formset):
        print(form.errors)
        print('-------------')
        print(formset.errors)
        print('-------------')
        print(near_formset.errors)
        print('-------------')
        print(seo_form.errors)
        context = {
            'formset': formset,
            'form': form,
            'near_formset': near_formset,
            'seo_form': seo_form
        }
        return self.render_to_response(context)
