import json
from datetime import datetime
import xlwt
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin, FormView
from django.views.generic.list import MultipleObjectMixin
from account.forms import *
from account.models import *
from account.views import has_access_for_class, has_access
from admin_app.forms import *
from admin_app.models import *
from django.core.mail import send_mail
from django.core.mail import EmailMessage


# Create your views here.
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'



class StatisticData:

    def __init__(self):
        self.house_count = House.objects.all().count()
        self.owner_count = Owner.objects.filter(status='Активен').count()
        self.master_request_in_process_count = MasterRequest.objects.filter(status='в процессе').count()
        self.flat_count = Flat.objects.all().count()
        self.bankbook_count = BankBook.objects.all().count()
        self.master_request_new_count = MasterRequest.objects.filter(status='новое').count()
        self.incomes_expenses = self.get_incomes_expenses()
        self.sum_account_debts = sum(get_account_debts())
        self.sum_account_balance = sum(get_account_balance())
        self.state_cashbox = get_state_cashbox()

    def get_incomes_expenses(self):
        current_year = datetime.now().year
        labels = ['Янв.,', 'Фев.,', 'Мар.,', 'Апр.,', 'Май,', 'Июн.,', 'Июл.,', 'Авг.,', 'Сен.,', 'Окт.,', 'Нояб.,', 'Дек.,']
        labels = [label + str(current_year) for label in labels]
        data_incomes = []
        data_expenses = []
        for i in range(12):
            expenses = str(CashBox.objects.filter(type='расход', date__month=i+1).aggregate(Sum('amount_of_money'))\
                .get('amount_of_money__sum'))
            incomes = str(CashBox.objects.filter(type='приход', date__month=i+1).aggregate(Sum('amount_of_money')) \
                .get('amount_of_money__sum'))
            data_incomes.append(incomes)
            data_expenses.append(expenses)
        return {"labels": labels, "incomes": data_incomes, "expenses": data_expenses}


def error_403(request, exception):
    return render(request, 'admin_app/403_csrf.html')

class IndexView(UserPassesTestMixin, FormView):
    template_name = 'admin_app/statistic.html'


    def get_context_data(self, **kwargs):
        context = {'statistic': StatisticData()}
        return context

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.statistic


class FilterMixin(MultipleObjectMixin):
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        get_params = self.request.GET.dict()
        logger.info(get_params)
        if any(get_params):
            if 'date_range' in get_params and get_params['date_range'] != '':
                date_range = get_params['date_range'].split(' - ')
                qs = qs.filter(date__range=date_range)
            get_params.pop('date_range', None)
            for param, value in get_params.items():
                if param != 'q' and value != '':
                    logger.info(param)
                    if not param == 'page':
                        qs = qs.filter(**{param: value})
        return qs

    def get_form_kwargs(self, *args, **kwargs):
        # use GET parameters as the data
        kwargs = super().get_form_kwargs(*args, **kwargs)
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs


class CreateService(UserPassesTestMixin, CreateView):
    template_name = 'admin_app/settings/services.html'

    def get_context_data(self, **kwargs):
        context = {
            'formset': ServiceFormset(queryset=Service.objects.all(), prefix='service'),
            'unit_formset': UnitFormset(queryset=Unit.objects.all()),
            'service': [x.service for x in TariffService.objects.all()],
            'unit': [x.unit for x in TariffService.objects.all()]
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

    def test_func(self):
            profile = Profile.objects.get(user_id=self.request.user.id)
            role = Role.objects.get(name=profile.role)
            return role.service

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


class TariffList(UserPassesTestMixin, ListView):
    model = Tariff
    template_name = 'admin_app/settings/tariff/index.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.tariff


class CreateTariff(UserPassesTestMixin, CreateView):
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

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.tariff


class UpdateTariff(UserPassesTestMixin, UpdateView):
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

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.tariff


class CloneTariff(UserPassesTestMixin, UpdateView):
    model = Tariff
    template_name = 'admin_app/settings/tariff/create.html'
    success_url = '/admin_app/tariff_list/'

    def get_context_data(self, **kwargs):
        context = {
            'form': TariffCreateForm(instance=Tariff.objects.get(id=self.kwargs['pk'])),
            'formset': TariffServiceFormSet(queryset=TariffService.objects.filter(tariff=self.kwargs['pk']),
                                            prefix='tariffservice_set'),
            'name': Tariff.objects.get(id=self.kwargs['pk']).name,
            'id': self.kwargs['pk']
        }
        return context

    def post(self, request, *args, **kwargs):
        formset = TariffServiceFormSet(request.POST, queryset=TariffService.objects.none(), prefix='tariffservice_set')
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


class ShowTariff(UserPassesTestMixin, DetailView):
    model = Tariff
    template_name = 'admin_app/settings/tariff/tariff.html'
    context_object_name = 'tariff'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = TariffService.objects.filter(tariff=self.kwargs['pk'])
        return context

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.tariff


class RoleList(UserPassesTestMixin, ListView):
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

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.role


class UserList(UserPassesTestMixin, ListView):
    model = Profile
    template_name = 'admin_app/settings/user/index.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.users



class CreateUser(UserPassesTestMixin, CreateView):
    model = Profile
    template_name = 'admin_app/settings/user/update.html'
    user = User()
    profile = Profile()

    def get_context_data(self, **kwargs):
        context = {
            'profile_form': ProfileChangeForm(),
            'register_form': UserChangeForm()
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


    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.users


class UpdateUser(UserPassesTestMixin, UpdateView):
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
            'profile_form': form_profile.errors,
            'register_form': form_user.errors
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.users


class ShowProfile(UserPassesTestMixin, DetailView):
    model = User
    template_name = 'admin_app/settings/user/profile.html'
    context_object_name = 'user'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.users


def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    profile = user.profile
    user.delete()
    profile.delete()
    return redirect('/admin_app/user_list/')


class PaymentDetailsView(UserPassesTestMixin, DetailView):
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

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.requisites


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


class MainPageView(UserPassesTestMixin, CreateView):
    template_name = 'admin_app/pages/main_page.html'
    try:
        instance = MainPage.objects.all()[0]
        instance_seo = instance.seo
    except:
        instance = None
        instance_seo = None

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
        form.save()
        seo_form.save()
        for form in formset:
            form.save()
        for n_form in near_formset:
            n_form.save()
        return redirect('/admin_app/main_page/')

    def form_invalid(self, form, seo_form, formset, near_formset):
        context = {
            'formset': formset,
            'form': form,
            'near_formset': near_formset,
            'seo_form': seo_form
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.site_management


class InfoPage(UserPassesTestMixin, CreateView):
    template_name = 'admin_app/pages/info_page.html'
    try:
        instance = Info.objects.all()[0]
    except:
        instance = None

    def get_context_data(self, **kwargs):
        form = InfoForm(instance=self.instance)
        formset = GalleryFormSet(queryset=Gallery.objects.filter(additional=False), prefix='gallery')
        extra_formset = ExtraGalleryFormSet(queryset=Gallery.objects.filter(additional=True), prefix='extra_gallery')
        doc_formset = DocumentFormSet(queryset=Document.objects.all(), prefix='doc')
        seo_form = SeoCreateForm(instance=self.instance.seo, prefix='seo')
        context = {
            'form': form,
            'formset': formset,
            'doc_formset': doc_formset,
            'seo_form': seo_form,
            'extra_formset': extra_formset
        }
        return context

    def post(self, request, *args, **kwargs):
        form = InfoForm(request.POST, request.FILES, instance=self.instance)
        formset = GalleryFormSet(request.POST, request.FILES, queryset=Gallery.objects.filter(additional=False), prefix='gallery')
        extra_formset = ExtraGalleryFormSet(request.POST, request.FILES, queryset=Gallery.objects.filter(additional=True), prefix='extra_gallery')
        doc_formset = DocumentFormSet(request.POST, request.FILES, queryset=Document.objects.all(), prefix='doc')
        seo_form = SeoCreateForm(request.POST, instance=self.instance.seo, prefix='seo')
        if form.is_valid() and formset.is_valid() and doc_formset.is_valid() and seo_form.is_valid() and extra_formset.is_valid():
            return self.form_valid(form, formset, doc_formset, seo_form, extra_formset)
        else:
            return self.form_invalid(form, formset, doc_formset, seo_form, extra_formset)

    def form_valid(self, form, formset, doc_formset, seo_form, extra_formset):
        form.save()
        doc_formset.save()
        seo_form.save()
        for x in extra_formset:
            form = x.save()
            form.additional = True
            form.save()
        for q in formset:
            form = q.save()
            form.additional = False
            form.save()
        return redirect('/admin_app/info_page/')

    def form_invalid(self, form, formset, doc_formset, seo_form, extra_formset):
        context = {
            'form': form,
            'formset': formset,
            'doc_formset': doc_formset,
            'seo_form': seo_form,
            'extra_formset': extra_formset
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.site_management


def delete_document(request, pk):
    Document.objects.get(pk=pk).delete()
    return redirect('/admin_app/info_page/')


def delete_from_gallery(request, image_id):
    Gallery.objects.get(id=image_id).delete()
    return redirect('/admin_app/info_page/')


class ServicePageView(UserPassesTestMixin, CreateView):
    template_name = 'admin_app/pages/service_page.html'
    try:
        instance = ServicePage.objects.all()[0]
    except:
        instance = None

    def get_context_data(self, **kwargs):
        formset = ServiceBlockFormSet(queryset=ServiceBlock.objects.all())
        seo_form = SeoCreateForm(instance=self.instance.seo)
        context = {
            'formset': formset,
            'seo_form': seo_form,
        }
        return context

    def post(self, request, *args, **kwargs):
        formset = ServiceBlockFormSet(request.POST, request.FILES, queryset=ServiceBlock.objects.all())
        seo_form = SeoCreateForm(request.POST, instance=self.instance.seo)
        if formset.is_valid() and seo_form.is_valid():
            return self.form_valid(formset, seo_form)
        else:
            return self.form_invalid(formset, seo_form)

    def form_valid(self, formset, seo_form):
        formset.save()
        seo_form.save()
        return redirect('/admin_app/service_page/')

    def form_invalid(self, formset, seo_form):
        print(formset.errors)
        context = {
            'formset': formset,
            'seo_form': seo_form,
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.site_management


def delete_service_page(request, service_id):
    ServiceBlock.objects.filter(id=service_id).delete()
    return redirect('/admin_app/service_page/')


class ContactPageView(UserPassesTestMixin, CreateView):
    template_name = 'admin_app/pages/contact_page.html'
    try:
        instance = ContactPage.objects.all()[0]
    except:
        instance = None

    def get_context_data(self, **kwargs):
        form = ContactPageForm(instance=self.instance, prefix='form')
        seo_form = SeoCreateForm(instance=self.instance.seo, prefix='seo')
        context = {
            'form': form,
            'seo_form': seo_form,
        }
        return context

    def post(self, request, *args, **kwargs):
        form = ContactPageForm(request.POST, instance=self.instance, prefix='form')
        seo_form = SeoCreateForm(request.POST, instance=self.instance.seo, prefix='seo')
        if form.is_valid() and seo_form.is_valid():
            return self.form_valid(form, seo_form)
        else:
            return self.form_invalid(form, seo_form)

    def form_valid(self, form, seo_form):
        form.save()
        seo_form.save()
        return redirect('/admin_app/contact_page/')

    def form_invalid(self, form, seo_form):
        context = {
            'form': form,
            'seo_form': seo_form,
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.site_management


class OwnerList(UserPassesTestMixin, FormMixin, ListView):
    paginate_by = 10
    model = Owner
    form_class = OwnerFilterForm
    template_name = 'admin_app/owner/index.html'



    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.owner


class CreateOwner(UserPassesTestMixin, CreateView):
    template_name = 'admin_app/owner/update.html'

    def get_context_data(self, **kwargs):
        context = {
            'user_form': UserChangeForm(),
            'owner_form': OwnerChangeForm(prefix='owner')
        }
        return context

    def post(self, request, *args, **kwargs):
        form_user = UserChangeForm(request.POST)
        owner_form = OwnerChangeForm(request.POST, request.FILES, prefix='owner')
        if form_user.is_valid() and owner_form.is_valid():
            return self.form_valid(form_user, owner_form)
        else:
            return self.form_invalid(form_user, owner_form)

    def form_valid(self, form_user, owner_form):
        created_user = form_user.save(commit=False)
        created_user.username = form_user.cleaned_data['email']
        created_user.set_password(form_user.cleaned_data['password'])
        created_user.save()

        created_owner = owner_form.save(commit=False)
        created_owner.user_id = created_user.id
        created_owner.save()
        return redirect('/admin_app/owner_list')

    def form_invalid(self, form_user, owner_form):
        context = {
            'user_form': form_user.errors,
            'owner_form': owner_form.errors
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.owner


class UpdateOwner(UserPassesTestMixin, UpdateView):
    model = Owner
    template_name = 'admin_app/owner/update.html'

    def get_context_data(self, **kwargs):
        owner = Owner.objects.get(user_id=self.kwargs['pk'])
        context = {
            'owner_form': OwnerChangeForm(instance=owner),
            'user_form': UserChangeForm(instance=owner.user)
        }
        return context

    def post(self, request, *args, **kwargs):
        owner = Owner.objects.get(user_id=self.kwargs['pk'])
        user_form = UserChangeForm(request.POST, instance=owner.user)
        owner_form = OwnerChangeForm(request.POST, request.FILES, instance=owner)
        if user_form.is_valid() and owner_form.is_valid():
            return self.form_valid(user_form, owner_form)
        else:
            return self.form_invalid(user_form, owner_form)

    def form_valid(self, user_form, owner_form):
        owner = Owner.objects.get(user_id=self.kwargs['pk'])
        psw = owner.user.password
        created_user = user_form.save()
        created_user.username = user_form.cleaned_data['email']
        if 'password' in user_form.changed_data and user_form.cleaned_data['password'] != '':
            created_user.set_password(user_form.cleaned_data['password'])
        else:
            created_user.set_password(psw)
        created_user.save()
        owner_form.save()
        return redirect('/admin_app/owner_list')

    def form_invalid(self, user_form, owner_form):
        """If the form is invalid, render the invalid form."""
        context = {
            'owner_form': owner_form,
            'user_form': user_form
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.owner


class DetailOwner(UserPassesTestMixin, DetailView):
    model = Owner
    template_name = 'admin_app/owner/detail.html'
    context_object_name = 'owner'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.owner


def delete_owner(request, owner_id):
    Owner.objects.filter(user_id=owner_id).update(status=Owner.Status.disabled)
    return redirect('/admin_app/owner_list/')


class InviteView(CreateView):
    template_name = 'admin_app/owner/invite.html'

    def get_context_data(self, **kwargs):
        context = {'form': InviteForm()}
        return context

    def post(self, request, *args, **kwargs):
        form = InviteForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return redirect('/admin_app/owner_list/')

    def form_valid(self, form):
        print(form.cleaned_data['mail'])
        send_mail(
            'MyHouse24',
            message='We glad to invite you on MyHouse24!',
            from_email='MyHouse24',
            recipient_list=[f'{form.cleaned_data["mail"]}'],
        )
        return redirect('/admin_app/owner_list/')


class HouseList(UserPassesTestMixin, FormMixin, FilterMixin, ListView):
    model = House
    form_class = HouseFilterForm
    template_name = 'admin_app/house/index.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.house


class CreateHouse(UserPassesTestMixin, CreateView):
    template_name = 'admin_app/house/update.html'

    def get_context_data(self, **kwargs):
        form = HouseCreateForm()
        section_formset = SectionFormSet(prefix='section')
        level_formset = LevelFormSet(prefix='level')
        user_formset = HouseUserFormSet(prefix='user')
        context = {
            "form": form,
            "section_formset": section_formset,
            "level_formset": level_formset,
            "user_formset": user_formset
        }
        return context

    def post(self, request, *args, **kwargs):
        form = HouseCreateForm(request.POST, request.FILES)
        if form.is_valid():
            created = form.save(commit=False)
            created.save()
            section_formset = SectionFormSet(request.POST, instance=created, prefix='section')
            level_formset = LevelFormSet(request.POST, instance=created, prefix='level')
            user_formset = HouseUserFormSet(request.POST, instance=created, prefix='user')
            if section_formset.is_valid() and level_formset.is_valid() and user_formset.is_valid():
                section_formset.save()
                level_formset.save()
                user_formset.save()
                return redirect('/admin_app/house_list')
            else:
                return self.form_invalid(form, section_formset, level_formset, user_formset)
        else:
            return self.render_to_response({'form': form.errors})

    def form_invalid(self, form, section_formset, level_formset, user_formset):
        context = {
            "form": form.errors,
            "section_formset": section_formset.errors,
            "level_formset": level_formset.errors,
            "user_formset": user_formset.errors
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.house


class UpdateHouse(UserPassesTestMixin, UpdateView):
    model = House
    template_name = 'admin_app/house/update.html'

    def get_context_data(self, **kwargs):
        instance = House.objects.get(id=self.kwargs['pk'])
        form = HouseCreateForm(instance=instance)
        section_formset = SectionFormSet(instance=instance, prefix='section')
        level_formset = LevelFormSet(instance=instance, prefix='level')
        user_formset = HouseUserFormSet(instance=instance, prefix='user')
        context = {
            "form": form,
            "section_formset": section_formset,
            "level_formset": level_formset,
            "user_formset": user_formset
        }
        return context

    def post(self, request, *args, **kwargs):
        instance = House.objects.get(id=self.kwargs['pk'])
        form = HouseCreateForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            created = form.save(commit=False)
            created.save()
            section_formset = SectionFormSet(request.POST, instance=created, prefix='section')
            level_formset = LevelFormSet(request.POST, instance=created, prefix='level')
            user_formset = HouseUserFormSet(request.POST, instance=created, prefix='user')
            if section_formset.is_valid() and level_formset.is_valid() and user_formset.is_valid():
                section_formset.save()
                level_formset.save()
                user_formset.save()
                return redirect('/admin_app/house_list')
            else:
                return self.form_invalid(form, section_formset, level_formset, user_formset)
        else:
            return self.render_to_response({'form': form.errors})

    def form_invalid(self, form, section_formset, level_formset, user_formset):
        context = {
            "form": form.errors,
            "section_formset": section_formset.errors,
            "level_formset": level_formset.errors,
            "user_formset": user_formset.errors
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.house


class HouseDetail(UserPassesTestMixin, DetailView):
    model = House
    template_name = 'admin_app/house/detail.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.house


def delete_house(request, house_id):
    House.objects.get(id=house_id).delete()
    return redirect('/admin_app/house_list')


class FlatList(UserPassesTestMixin, FormMixin, ListView):
    paginate_by = 10
    model = Flat
    template_name = 'admin_app/flat/index.html'
    form_class = FlatFilterForm

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.apartment


def get_section_level(request):
    if is_ajax(request):
        house = request.GET.get('house')
        sections = Section.objects.filter(house_id=house).values('name', 'id')
        levels = Level.objects.filter(house_id=house).values('name', 'id')
        return JsonResponse(json.dumps({'sections': list(sections), 'levels': list(levels)}), safe=False)


class CreateFlat(UserPassesTestMixin, CreateView):
    model = Flat
    template_name = 'admin_app/flat/update.html'

    def get_context_data(self, **kwargs):
        form = FlatCreateForm()
        context = {
            'form': form
        }
        return context

    def post(self, request, *args, **kwargs):
        form = FlatCreateForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        flat = form.save(commit=False)
        if 'bank_book' in form.changed_data:
            bankbook = BankBook.objects.get(id=form.cleaned_data['bank_book'])
            flat.save()
            bankbook.flat_id = flat.id
            bankbook.save()
        else:
            flat.save()
        return redirect('/admin_app/flat_list')

    def form_invalid(self, form):
        context = {
            'form': form.errors
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.apartment


class UpdateFlat(UserPassesTestMixin, UpdateView):
    model = Flat
    template_name = 'admin_app/flat/update.html'

    def get_context_data(self, **kwargs):
        form = FlatCreateForm(instance=Flat.objects.get(id=self.kwargs['pk']))
        context = {
            'form': form,
            "update": True,
        }
        try:
            context['bankbook'] = BankBook.objects.get(flat_id=self.kwargs['pk'])
        except:
            pass

        return context

    def post(self, request, *args, **kwargs):
        form = FlatCreateForm(request.POST, instance=Flat.objects.get(id=self.kwargs['pk']))
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        flat = form.save(commit=False)
        if 'bank_book' in form.changed_data:
            bankbook = BankBook.objects.get(id=form.cleaned_data['bank_book'])
            flat.save()
            bankbook.flat_id = flat.id
            bankbook.save()
        else:
            flat.save()
        return redirect('/admin_app/flat_list')

    def form_invalid(self, form):
        context = {
            'form': form.errors
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.apartment


class FlatDetail(UserPassesTestMixin, DetailView):
    model = Flat
    template_name = 'admin_app/flat/detail.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.apartment


def delete_flat(request, pk):
    Flat.objects.get(pk=pk).delete()
    return redirect('/admin_app/flat_list')


def get_account_debts():
    balances = []
    for bankbook in BankBook.objects.filter(status='Активен'):
        if bankbook.balance() < 0:
            balances.append(math.fabs(bankbook.balance()))
    return balances


def get_account_balance():
    balances = []
    for bankbook in BankBook.objects.filter(status='Активен'):
        if bankbook.balance() > 0:
            balances.append(math.fabs(bankbook.balance()))
    return balances


def get_state_cashbox():
    expenses = str(CashBox.objects.filter(type='расход').aggregate(Sum('amount_of_money')).get('amount_of_money__sum'))
    incomes = str(CashBox.objects.filter(type='приход').aggregate(Sum('amount_of_money')).get('amount_of_money__sum'))
    print('incomes: ' + incomes, ' expenses: ' + expenses)
    try:
        return float(incomes) - float(expenses)
    except ValueError:
        return None


class StatisticMixin(MultipleObjectMixin):

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(StatisticMixin, self).get_context_data(**kwargs)
        context['account_debts'] = sum(get_account_debts())
        context['account_balance'] = sum(get_account_balance())
        context['state_cashbox'] = get_state_cashbox()
        return context


class CounterView(UserPassesTestMixin, FilterMixin, FormMixin, ListView):
    paginate_by = 10
    model = Counter
    template_name = 'admin_app/counter/index.html'
    form_class = CounterFilterForm

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.meter


def filter_flat_counter(flat, params):
    counters = Counter.objects.filter(
        flat=flat
    )
    if 'date' in params and params['date'] != '':
        date_range = params['date'].split(' - ')
        counters = counters.filter(date__range=date_range)
    params.pop('date', None)
    for param, value in params.items():
        if param != 'q' and value != '':
            counters = counters.filter(**{param: value})
    return counters


class FlatCounterList(UserPassesTestMixin, FormMixin, ListView):
    model = Flat
    template_name = 'admin_app/counter/flat_counter.html'
    form_class = FlatCounterFilterForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        get_params = self.request.GET.dict()
        if any(get_params):
            context_data['counter_list'] = filter_flat_counter(self.kwargs['pk'], get_params)
        else:
            context_data['counter_list'] = self.object.counter_set.all()

        context_data['flat'] = self.kwargs['pk']
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.meter


class CreateCounter(UserPassesTestMixin, CreateView):
    model = Counter
    template_name = 'admin_app/counter/update.html'

    def get_context_data(self, **kwargs):
        print(self.request.GET)
        form = CounterCreateForm()
        context = {
            'form': form
        }
        if self.request.GET.get('flat'):
            context['get_params'] = self.request.GET.dict()

        return context

    def post(self, request, *args, **kwargs):
        form = CounterCreateForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return redirect('/admin_app/counter_list')

    def form_invalid(self, form):
        context = {
            'form': form.errors
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.meter


def get_section_flat(request):
    if is_ajax(request):
        house = request.GET.get('house')
        sections = Section.objects.filter(house_id=house).values('name', 'id')
        flats = Flat.objects.filter(house_id=house).values('number', 'id')
        return JsonResponse(json.dumps({'sections': list(sections), 'flats': list(flats)}), safe=False)


def get_flats(request):
    if is_ajax(request):
        if 'section' in request.GET.dict():
            section = request.GET.get('section')
            flats = Flat.objects.filter(section_id=section).values('number', 'id')
        else:
            level = request.GET.get('level')
            flats = Flat.objects.filter(level_id=level).values('number', 'id')
        return JsonResponse(json.dumps({'flats': list(flats)}), safe=False)


def get_flats_by_owner(request):
    if is_ajax(request):
        owner = request.GET.get('owner')
        flats = Flat.objects.filter(owner_id=owner).values('number', 'id', 'house__name')
        return JsonResponse(json.dumps({'flats': list(flats)}), safe=False)


class UpdateCounter(UserPassesTestMixin, UpdateView):
    model = Counter
    template_name = 'admin_app/counter/update.html'

    def get_context_data(self, **kwargs):
        instance = Counter.objects.get(id=self.kwargs['pk'])
        form = CounterCreateForm(instance=instance)
        flat = Flat.objects.get(id=instance.flat_id)
        context = {"form": form,
                   "update": True,
                   "house": House.objects.get(id=flat.house_id)
                   }
        return context

    def post(self, request, *args, **kwargs):
        form = CounterCreateForm(request.POST, instance=Counter.objects.get(id=self.kwargs['pk']))
        if form.is_valid():
            form.save()
            return redirect('/admin_app/counter_list')
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = {
            'form': form.errors
        }
        return self.render_to_response(context)

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.meter


class CounterDetail(UserPassesTestMixin, DetailView):
    model = Counter
    template_name = 'admin_app/counter/detail.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.meter


def delete_counter(request, counter_id):
    Counter.objects.get(id=counter_id).delete()
    return redirect('/admin_app/counter_list')


class CashBoxMixin(MultipleObjectMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_income = CashBox.objects.filter(status=True, type='приход').aggregate(Sum('amount_of_money')).get('amount_of_money__sum', 0.00)
        total_expenses = CashBox.objects.filter(status=True, type='расход').aggregate(Sum('amount_of_money')).get('amount_of_money__sum', 0.00)
        context['total_income'] = total_income if total_income else 0
        context['total_expenses'] = total_expenses if total_expenses else 0
        return context


class CashBoxList(UserPassesTestMixin, StatisticMixin, FormMixin, FilterMixin, CashBoxMixin, ListView):
    paginate_by = 10
    model = CashBox
    template_name = 'admin_app/cash_box/index.html'
    form_class = CashBoxFilterForm

    def get_form_kwargs(self):
        # use GET parameters as the data
        kwargs = super().get_form_kwargs()
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.cash_box


class CashBoxDetail(UserPassesTestMixin, DetailView):
    model = CashBox
    template_name = 'admin_app/cash_box/detail.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.cash_box


class CreateIncome(UserPassesTestMixin, CreateView):
    model = CashBox
    template_name = 'admin_app/cash_box/update_income.html'

    def get(self, request):
        if request.GET.get('bankbook_id'):
            instance = BankBook.objects.get(id=request.GET.get('bankbook_id'))
            return self.render_to_response(self.get_context_data(instance))
        return self.render_to_response(self.get_context_data())


    def get_context_data(self, *args, **kwargs):
        form = CashBoxIncomeCreateForm()
        context = {'form': form}
        if args:
            flat = Flat.objects.get(id=args[0].flat_id)
            context['bankbook'] = args[0]
            context['owner'] = Owner.objects.get(user_id=flat.owner_id)
            context['flat_create'] = True
        return context

    def post(self, request, *args, **kwargs):
        form = CashBoxIncomeCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/cashbox_list')

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.cash_box


class UpdateIncome(UserPassesTestMixin, UpdateView):
    model = CashBox
    template_name = 'admin_app/cash_box/update_income.html'

    def get_context_data(self, **kwargs):
        instance = CashBox.objects.get(id=self.kwargs['pk'])
        form = CashBoxIncomeCreateForm(instance=instance)
        try:
            bankbook = BankBook.objects.get(id=instance.bankbook_id)
            flat = Flat.objects.get(id=bankbook.flat_id)
            owner = Owner.objects.get(user_id=flat.owner_id)
        except:
            bankbook = ''
            flat = ''
            owner = ''

        context = {'form': form, 'update': True, 'owner': owner}
        return context

    def post(self, request, *args, **kwargs):
        instance = CashBox.objects.get(id=self.kwargs['pk'])
        form = CashBoxIncomeCreateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/cashbox_list')

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.cash_box


class CreateExpense(UserPassesTestMixin, CreateView):
    model = CashBox
    template_name = 'admin_app/cash_box/update_expense.html'

    def get_context_data(self, **kwargs):
        form = CashBoxExpenseCreateForm()
        context = {'form': form}
        return context

    def post(self, request, *args, **kwargs):
        form = CashBoxExpenseCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/cashbox_list')
        else:
            print(form.errors)
            return self.render_to_response({'form': form.errors})

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.cash_box


class UpdateExpense(UserPassesTestMixin, UpdateView):
    model = CashBox
    template_name = 'admin_app/cash_box/update_expense.html'

    def get_context_data(self, **kwargs):
        instance = CashBox.objects.get(id=self.kwargs['pk'])
        form = CashBoxExpenseCreateForm(instance=instance)
        context = {'form': form, 'update': True}
        return context

    def post(self, request, *args, **kwargs):
        instance = CashBox.objects.get(id=self.kwargs['pk'])
        form = CashBoxExpenseCreateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/cashbox_list')

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.cash_box


def write_columns(ws, columns, font_style, row_num):
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
        col = ws.col(col_num)
        col.width = 256*(len(columns[col_num])+5)


def export_cashbox(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="cashbox.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('sheet1')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['#', 'Дата', 'Приход/расход', 'Статус', 'Статья', 'Сумма', 'Владелец квартиры', 'Лицевой счет']
    write_columns(ws, columns, font_style, row_num)
    font_style = xlwt.XFStyle()

    rows = CashBox.objects.all().values_list('id', 'date', 'type', 'status', 'payment_type__name',
                                             'amount_of_money', 'bankbook__flat__owner', 'bankbook')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num == 6 and Owner.objects.filter(user_id=row[col_num]).exists():
                owner = Owner.objects.get(user_id=row[col_num])
                ws.write(row_num, col_num, owner.fullname(), font_style)
                col = ws.col(col_num)
                if col.width < 256 * len(owner.fullname()):
                    col.width = 256 * (len(owner.fullname()) + 5)
                continue
            elif row[col_num] is None:
                continue
            ws.write(row_num, col_num, str(row[col_num]), font_style)
            col = ws.col(col_num)
            if col.width < 256 * len(str(row[col_num])):
                col.width = 256 * (len(str(row[col_num])) + 5)
    wb.save(response)
    return response


def delete_cash_box(request, cash_box_id):
    CashBox.objects.get(id=cash_box_id).delete()
    return redirect('/admin_app/cashbox_list')


class BankBookList(UserPassesTestMixin, StatisticMixin, FormMixin, ListView):
    paginate_by = 10
    model = BankBook
    template_name = 'admin_app/bank_book/index.html'
    form_class = BankBookFilterForm

    def get_queryset(self):
        qs = super(BankBookList, self).get_queryset()
        get_params = self.request.GET.dict()
        logger.info(get_params)
        if any(get_params):
            if get_params['id'] != '':
                qs = qs.filter(id__icontains=get_params['id'])
                del get_params['id']
                logger.info(get_params)
            for param, value in get_params.items():
                if param != 'q' and value != '':
                    logger.info(param)
                    qs = qs.filter(**{param: value})
        return qs

    def get_form_kwargs(self):
        # use GET parameters as the data
        kwargs = super().get_form_kwargs()
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.personal_account


class CreateBankBook(UserPassesTestMixin, CreateView):
    model = BankBook
    template_name = 'admin_app/bank_book/update.html'

    def get_context_data(self, **kwargs):
        form = BankbookCreateForm()
        context = {'form': form}
        return context

    def post(self, request, *args, **kwargs):
        form = BankbookCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/bankbook_list')

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.personal_account


class UpdateBankBook(UserPassesTestMixin, UpdateView):
    model = BankBook
    template_name = 'admin_app/bank_book/update.html'

    def get_context_data(self, **kwargs):
        instance = BankBook.objects.get(id=self.kwargs['pk'])
        form = BankbookCreateForm(instance=instance)
        try:
            flat = Flat.objects.get(id=instance.flat_id)
            house = House.objects.get(id=flat.house_id)
            exist = True
            context = {'form': form, 'update': exist, 'bankbook': flat, "house": house}
        except:
            context = {'form': form}
        return context

    def post(self, request, *args, **kwargs):
        instance = BankBook.objects.get(id=self.kwargs['pk'])
        form = BankbookCreateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/bankbook_list')

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.personal_account


def delete_bankbook(request, bankbook_id):
    BankBook.objects.get(id=bankbook_id).delete()
    return redirect('/admin_app/bankbook_list')


class BankbookDetail(UserPassesTestMixin, DetailView):
    model = BankBook
    template_name = 'admin_app/bank_book/detail.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.personal_account


def get_owner(request):
    if is_ajax(request):
        flat = Flat.objects.get(id=request.GET.get('flat'))
        bankbook = flat.bankbook_set.first()
        owner = Owner.objects.get(user_id=flat.owner_id)
        try:
            response = {'id': owner.user_id, 'fullname': owner.fullname(), 'phone': owner.phone,
                        'bankbook': bankbook.id, 'tariff': flat.tariff_id}
        except AttributeError:
            response = {'id': owner.user_id, 'fullname': owner.fullname(), 'phone': owner.phone}
        return JsonResponse(json.dumps({'owner': response}), safe=False)


def export_bankbook(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="accounts.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('sheet1')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Лицевой счет', 'Статус', 'Дом', 'Секция', 'Квартира', 'Владелец', 'Остаток']
    write_columns(ws, columns, font_style, row_num)
    font_style = xlwt.XFStyle()

    rows = BankBook.objects.all().values_list('id', 'status', 'flat__house__name', 'flat__house__section__name',
                                              'flat__number', 'flat__owner')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num == 5 and Owner.objects.filter(user_id=row[col_num]).exists():
                owner = Owner.objects.get(user_id=row[col_num])
                ws.write(row_num, col_num, owner.fullname(), font_style)
                col = ws.col(col_num)
                if col.width < 256 * len(owner.fullname()):
                    col.width = 256 * (len(owner.fullname()) + 5)
                continue
            elif row[col_num] is None:
                continue
            ws.write(row_num, col_num, str(row[col_num]), font_style)
            col = ws.col(col_num)
            if col.width < 256 * len(str(row[col_num])):
                col.width = 256 * (len(str(row[col_num])) + 5)
    wb.save(response)
    return response


def get_bankbooks(request):
    if is_ajax(request):
        bankbooks = BankBook.objects.filter(flat__owner_id=request.GET.get('owner')).values('id')
        return JsonResponse(json.dumps({'bankbooks': list(bankbooks)}), safe=False)


def get_receipt_service_data(service: Service, tariff: Tariff):
    unit = service.unit_id
    try:
        unit_price = service.tariffservice_set.get(tariff_id=tariff.id).price
    except TariffService.DoesNotExist:
        unit_price = None
    return {'unit': unit, 'unit_price': unit_price}


def get_service(request):
    if is_ajax(request):
        if TariffService.objects.get(service_id=request.GET.get('service'), tariff_id=request.GET.get('tariff')):
            service = Service.objects.get(id=request.GET.get('service'))
            tariff = Tariff.objects.get(id=request.GET.get('tariff'))
            response = get_receipt_service_data(service, tariff)
            return JsonResponse(json.dumps({'service': response}), safe=False)


def get_counters(request):
    if is_ajax(request):
        print(request.GET.get('flat'), '55555555555')
        counters = Counter.objects.filter(flat_id=request.GET.get('flat')).\
            values('id', 'status', 'date', 'flat__house__name', 'flat__section__name', 'flat__number',
                   'service', 'indication', 'service__unit')
        return JsonResponse({'counters': list(counters)}, safe=False)


class ReceiptList(UserPassesTestMixin, FormMixin, FilterMixin, StatisticMixin, ListView):
    paginate_by = 10
    model = Receipt
    form_class = ReceiptFilterForm
    template_name = 'admin_app/receipt/index.html'

    def get_form_kwargs(self, *args, **kwargs):
        # use GET parameters as the data
        kwargs = super().get_form_kwargs(*args, **kwargs)
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.invoice


class CreateReceipt(UserPassesTestMixin, CreateView):
    model = Receipt
    template_name = 'admin_app/receipt/update.html'

    def get(self, request):
        if request.GET.get('flat_id'):
            instance = Flat.objects.get(id=request.GET.get('flat_id'))
            return self.render_to_response(self.get_context_data(instance))
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        form = ReceiptCreateForm()
        formset = ReceiptServiceFormSet(prefix='receiptservice_set')
        counters = Counter.objects.all()

        context = {
            'form': form,
            'formset': formset,
            'counters': counters,

        }
        if args:
            flat = args[0]
            house = House.objects.get(id=flat.house_id)
            section = Section.objects.get(id=flat.section_id)
            context['flat'] = flat
            context['house'] = house
            context['section'] = section
            context['update_flat'] = True
        return context

    def post(self, request, *args, **kwargs):
        created = ReceiptCreateForm(request.POST)
        if created.is_valid():
            created.save(commit=False)
            formset = ReceiptServiceFormSet(request.POST, instance=created.instance)
            if formset.is_valid():
                created.save()
                formset.save()
                return redirect('/admin_app/receipt_list')

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.invoice


class UpdateReceipt(UserPassesTestMixin, UpdateView):
    model = Receipt
    template_name = 'admin_app/receipt/update.html'

    def get_context_data(self, **kwargs):
        instance = Receipt.objects.get(id=self.kwargs['pk'])
        form = ReceiptCreateForm(instance=instance)
        formset = ReceiptServiceFormSet(instance=instance, prefix='receiptservice_set')
        counters = Counter.objects.filter(flat_id=instance.flat_id)
        flat = Flat.objects.get(id=instance.flat_id)
        house = House.objects.get(id=flat.house_id)
        section = Section.objects.get(id=flat.section_id)

        context = {
            'form': form,
            'formset': formset,
            'counters': counters,
            'house': house,
            'section': section,
            'update': True

        }
        return context

    def post(self, request, *args, **kwargs):
        instance = Receipt.objects.get(id=self.kwargs['pk'])
        created = ReceiptCreateForm(request.POST, instance=instance)
        if created.is_valid():
            created.save(commit=False)
            formset = ReceiptServiceFormSet(request.POST, instance=created.instance)
            if formset.is_valid():
                created.save()
                formset.save()
                return redirect('/admin_app/receipt_list')

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.invoice


class ReceiptDetail(UserPassesTestMixin, DetailView):
    model = Receipt
    template_name = 'admin_app/receipt/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ReceiptDetail, self).get_context_data(**kwargs)
        receipt = self.get_object()
        context['total'] = receipt.receiptservice_set.all(). \
            aggregate(Sum('price')).get('price__sum', 0.00)
        return context

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.invoice


def delete_receipt(request, receipt_id=None):
    if receipt_id:
        Receipt.objects.get(id=receipt_id).delete()
    else:
        logger.info(request.POST)
        Receipt.objects.filter(id__in=request.POST.getlist('ids[]')).delete()
    return redirect('/admin_app/receipt_list')


class MasterRequestList(UserPassesTestMixin, FormMixin, FilterMixin, ListView):
    paginate_by = 10
    model = MasterRequest
    template_name = 'admin_app/master_request/index.html'
    form_class = MasterRequestFilterForm
    ordering = ['-id']

    def get_form_kwargs(self):
        # use GET parameters as the data
        kwargs = super().get_form_kwargs()
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.application


class MasterRequestCreate(UserPassesTestMixin, CreateView):
    model = MasterRequest
    template_name = 'admin_app/master_request/create.html'
    form_class = MasterRequestForm
    success_url = reverse_lazy('master_request_list')

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.application


class MasterRequestUpdate(UserPassesTestMixin, UpdateView):
    model = MasterRequest
    template_name = 'admin_app/master_request/create.html'
    form_class = MasterRequestForm
    success_url = reverse_lazy('master_request_list')

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.application


class MasterRequestDetail(UserPassesTestMixin, DetailView):
    model = MasterRequest
    template_name = 'admin_app/master_request/detail.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.application


def delete_master_request(request, pk):
    MasterRequest.objects.get(id=pk).delete()
    return redirect('/admin_app/master_request_list')


class MessageList(UserPassesTestMixin, ListView):
    model = Message
    template_name = 'admin_app/message/index.html'
    ordering = ['-id']

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.message


class MessageCreate(UserPassesTestMixin, CreateView):
    model = Message
    template_name = 'admin_app/message/create.html'
    form_class = MessageForm
    success_url = reverse_lazy('message_list')

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        try:
            flat = Flat.objects.get(id=form.instance.flat_id)
            form.instance.owner_id = flat.owner_id
        except:
            return super().form_valid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        owner = self.request.GET.get('owner_id')
        context['owner'] = owner
        context['has_debt'] = self.request.GET.get('has_debt')
        return context

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.message


class MessageDetail(UserPassesTestMixin, DetailView):
    model = Message
    template_name = 'admin_app/message/detail.html'

    def test_func(self):
        profile = Profile.objects.get(user_id=self.request.user.id)
        role = Role.objects.get(name=profile.role)
        return role.message


def delete_message(request):
    print(request)
    logger.info(request.POST)
    Message.objects.filter(id__in=request.POST.getlist('ids[]')).delete()
    return redirect('/admin_app/message_list')


def write_rows(ws, columns, font_style):
    ct = len(columns)
    for row_num in range(ct):
        ws.write(row_num, 0, columns[row_num], font_style)
        col = ws.col(0)
        if col.width < 256 * len(str(columns[row_num])):
            col.width = 256 * (len(str(columns[row_num])) + 5)


def export_transaction(request, pk):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="transaction.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('sheet1')
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    _columns = ['Платеж', 'Дата', 'Владелец квартиры', 'Лицевой счет', 'Приход/расход', 'Статус', 'Статья', 'Квитанция',
                'Услуга', 'Сумма', 'Валюта', 'Комментарий', 'Менеджер']
    write_rows(ws, _columns, font_style)
    font_style = xlwt.XFStyle()

    cashbox = CashBox.objects.get(id=pk)
    try:
        bank_book = BankBook.objects.get(id=cashbox.bankbook_id)
    except:
        bank_book = False
    status = 'проведен' if cashbox.status else 'не проведен'
    _columns = [f'#{pk}', f'{cashbox.date}', bank_book.flat.owner.fullname() if bank_book else '', bank_book.id if bank_book else '', cashbox.type, status, cashbox.payment_type.name, 'Не задано',
                '',
                f'{cashbox.amount_of_money}',
                'UAH',
                cashbox.comment,
                cashbox.manager.fullname()]

    ct = len(_columns)
    for row_num in range(ct):
        if _columns[row_num] is None:
            continue
        ws.write(row_num, 1, _columns[row_num], font_style)
        col = ws.col(1)
        if col.width < 256 * len(str(_columns[row_num])):
            col.width = 256 * (len(str(_columns[row_num])) + 5)

    wb.save(response)
    return response


class TemplateChooseView(ListView):
    model = Template
    queryset = Template.objects.all()
    template_name = 'admin_app/receipt/template_download.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list)
        context['receipt'] = self.request.GET.get('receipt')
        return context


class ReceiptTemplateCreateView(CreateView):
    model = Template
    template_name = 'admin_app/receipt/template_create.html'
    form_class = ReceiptTemplateForm
    string_permission = 'receipt_access'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = Template.objects.all().order_by('id')
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/receipt/template_create/')
        return redirect('/admin_app/receipt/template_create/')


class ReceiptToEmailSend(CreateView):
    string_permission = 'receipt_access'

    def get(self, request, *args, **kwargs):
        file_path = self.request.GET.get('full_path')
        receipt = Receipt.objects.get(id=self.request.GET.get('receipt'))
        email = EmailMessage('Квитанция', to=[receipt.flat.owner.user.email])


        email.attach_file(file_path)
        if email.send():
            return JsonResponse({'answer': 'success'})
        else:
            return JsonResponse({'answer': 'none'})


class TemplateDefault(SingleObjectMixin, View):
    model = Template
    pk_url_kwarg = 'template_pk'

    def get_object(self, queryset=None):
        try:
            return Template.objects.get(pk=self.kwargs.get('template_pk'))
        except Template.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj:
            try:
                another_default = Template.objects.get(is_default=True)
                another_default.is_default = False
                another_default.save()
            except Template.DoesNotExist:
                pass
            obj.is_default = True
            obj.save()
            return redirect('/admin_app/receipt/template_create/')
        return redirect('/admin_app/receipt/template_create/')


def delete_template(request, template_id):
    logger.info(request.POST)
    Template.objects.get(id=template_id).delete()
    return redirect('/admin_app/receipt/template_create/')