from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView

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


# def services(request):
#     formset = ServiceFormset(request.POST or None, queryset=Service.objects.all(), prefix='service')
#     unit_formset = UnitFormset(request.POST or None, queryset=Unit.objects.all())
#
#     if request.method == 'POST':
#         if unit_formset.is_valid() and formset.is_valid:
#             unit_formset.save()
#             for form in formset:
#                 form.save()
#                 print(form)
#             return redirect('/admin_app/services/')
#
#     context = {
#         'formset': formset,
#         'unit_formset': unit_formset,
#     }
#     return render(request, 'admin_app/settings/services.html', context=context)


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
        formset = TariffServiceFormSet(request.POST or None, prefix='tariffservice_set')
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




# def create_tariff(request, tariff_id):
#     instance = None
#     _filter = None
#     if tariff_id != 0:
#         instance = Tariff.objects.get(id=tariff_id)
#     if TariffService.objects.filter(tariff=tariff_id):
#         _filter = tariff_id
#     form = TariffCreateForm(request.POST or None, instance=instance)
#     formset = TariffServiceFormSet(request.POST or None, queryset=TariffService.objects.filter(tariff=_filter), prefix='tariffservice_set')
#     if request.method == 'POST':
#         if form.is_valid():
#             tariff = form.save()
#             for form in formset:
#                 if form.is_valid():
#                     if form.cleaned_data:
#                         full_form = form.save()
#                         full_form.tariff = tariff
#                         full_form.unit = full_form.service.unit
#                         full_form.save()
#
#         return redirect('/admin_app/tariff_list/')
#
#     context = {
#         'form': form,
#         'formset': formset,
#     }
#     if instance:
#         context.update({'name': instance.name})
#     return render(request, 'admin_app/settings/tariff/create.html', context=context)


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




