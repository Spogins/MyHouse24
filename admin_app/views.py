import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin

from account.forms import *
from account.models import *
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


class CloneTariff(UpdateView):
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
        formset = TariffServiceFormSet(request.POST, queryset=None, prefix='tariffservice_set')
        form = TariffCreateForm(request.POST)
        if form.is_valid():
            return self.form_valid(formset, form)

    def form_valid(self, formset, form):
        tariff = form.save()
        for form in formset:
            if form.is_valid():
                if form.cleaned_data:
                    pass
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
    model = Profile
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
            'profile_form': form_profile.errors,
            'register_form': form_user.errors
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


class InfoPage(CreateView):
    template_name = 'admin_app/pages/info_page.html'
    instance = Info.objects.all()[0]

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


def delete_document(request, pk):
    Document.objects.get(pk=pk).delete()
    return redirect('/admin_app/info_page/')


def delete_from_gallery(request, image_id):
    Gallery.objects.get(id=image_id).delete()
    return redirect('/admin_app/info_page/')


class ServicePageView(CreateView):
    template_name = 'admin_app/pages/service_page.html'
    instance = ServicePage.objects.all()[0]

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
        print('---------')
        print(seo_form.errors)
        context = {
            'formset': formset,
            'seo_form': seo_form,
        }
        return self.render_to_response(context)


def delete_service_page(request, service_id):
    ServiceBlock.objects.filter(id=service_id).delete()
    return redirect('/admin_app/service_page/')


class ContactPageView(CreateView):
    template_name = 'admin_app/pages/contact_page.html'
    instance = ContactPage.objects.all()[0]

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


class OwnerList(ListView):
    model = Owner
    form_class = OwnerFilterForm
    template_name = 'admin_app/owner/index.html'


class CreateOwner(CreateView):
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


class UpdateOwner(UpdateView):
    model = Owner
    template_name = 'admin_app/owner/update.html'

    def get_context_data(self, **kwargs):
        owner = Owner.objects.get(user_id=self.kwargs['pk'])
        print(owner)
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
        created_user = user_form.save()
        created_user.username = user_form.cleaned_data['email']
        if user_form.cleaned_data['password']:
            created_user.set_password(user_form.cleaned_data['password'])
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


class DetailOwner(DetailView):
    model = Owner
    template_name = 'admin_app/owner/detail.html'
    context_object_name = 'owner'


def delete_owner(request, owner_id):
    Owner.objects.filter(user_id=owner_id).update(status=Owner.Status.disabled)
    return redirect('/admin_app/owner_list/')


class InviteView(CreateView):
    template_name = 'admin_app/owner/invite.html'

    def get_context_data(self, **kwargs):
        context = {'form': InviteForm()}
        return context


class MessageCreate(CreateView):
    pass


class HouseList(ListView):
    model = House
    form_class = HouseFilterForm
    template_name = 'admin_app/house/index.html'


class CreateHouse(CreateView):
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


class UpdateHouse(UpdateView):
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


class HouseDetail(DetailView):
    model = House
    template_name = 'admin_app/house/detail.html'


def delete_house(request, house_id):
    House.objects.get(id=house_id).delete()
    return redirect('/admin_app/house_list')


class FlatList(ListView):
    model = Flat
    template_name = 'admin_app/flat/index.html'
    form_class = FlatFilterForm


def get_section_level(request):
    if is_ajax(request):
        house = request.GET.get('house')
        sections = Section.objects.filter(house_id=house).values('name', 'id')
        levels = Level.objects.filter(house_id=house).values('name', 'id')
        return JsonResponse(json.dumps({'sections': list(sections), 'levels': list(levels)}), safe=False)


class CreateFlat(CreateView):
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
        return redirect('admin_app/flat_list')

    def form_invalid(self, form):
        context = {
            'form': form.errors
        }
        return self.render_to_response(context)


class UpdateFlat(UpdateView):
    model = Flat
    template_name = 'admin_app/flat/update.html'

    def get_context_data(self, **kwargs):
        form = FlatCreateForm(instance=Flat.objects.get(id=self.kwargs['pk']))
        context = {
            'form': form
        }
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


class FlatDetail(DetailView):
    model = Flat
    template_name = 'admin_app/flat/detail.html'


def delete_flat(request, pk):
    Flat.objects.get(pk=pk).delete()
    return redirect('/admin_app/flat_list')


class CounterView(ListView):
    model = Counter
    template_name = 'admin_app/counter/index.html'
    form_class = CounterFilterForm


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


class FlatCounterList(ListView):
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


class CreateCounter(CreateView):
    model = Counter
    template_name = 'admin_app/counter/update.html'

    def get_context_data(self, **kwargs):
        form = CounterCreateForm()
        context = {
            'form': form
        }
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


class UpdateCounter(UpdateView):
    model = Counter
    template_name = 'admin_app/counter/update.html'

    def get_context_data(self, **kwargs):
        instance = Counter.objects.get(id=self.kwargs['pk'])
        form = CounterCreateForm(instance=instance)
        flat = Flat.objects.get(id=instance.flat_id)
        context = {"form": form,
                   "update": True,
                   "house": flat.house_id
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


class CounterDetail(DetailView):
    model = Counter
    template_name = 'admin_app/counter/detail.html'


def delete_counter(request, counter_id):
    Counter.objects.get(id=counter_id).delete()
    return redirect('/admin_app/counter_list')


class CashBoxList(ListView):
    model = CashBox
    template_name = 'admin_app/cash_box/index.html'
    form_class = CashBoxFilterForm


class CashBoxDetail(DetailView):
    model = CashBox
    template_name = 'admin_app/cash_box/detail.html'


class CreateIncome(CreateView):
    model = CashBox
    template_name = 'admin_app/cash_box/update_income.html'

    def get_context_data(self, **kwargs):
        form = CashBoxIncomeCreateForm()
        context = {'form': form}
        return context

    def post(self, request, *args, **kwargs):
        form = CashBoxIncomeCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/cashbox_list')


class UpdateIncome(UpdateView):
    model = CashBox
    template_name = 'admin_app/cash_box/update_income.html'

    def get_context_data(self, **kwargs):
        instance = CashBox.objects.get(id=self.kwargs['pk'])
        form = CashBoxIncomeCreateForm(instance=instance)
        context = {'form': form, 'update': True}
        return context

    def post(self, request, *args, **kwargs):
        instance = CashBox.objects.get(id=self.kwargs['pk'])
        form = CashBoxIncomeCreateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/cashbox_list')


class CreateExpense(CreateView):
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


class UpdateExpense(UpdateView):
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



def export_cashbox(request):
    pass


def delete_cash_box(request, cash_box_id):
    CashBox.objects.get(id=cash_box_id).delete()
    return redirect('/admin_app/cashbox_list')


class BankBookList(ListView):
    model = BankBook
    template_name = 'admin_app/bank_book/index.html'
    form_class = BankBookFilterForm


class CreateBankBook(CreateView):
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


class UpdateBankBook(UpdateView):
    model = BankBook
    template_name = 'admin_app/bank_book/update.html'

    def get_context_data(self, **kwargs):
        instance = BankBook.objects.get(id=self.kwargs['pk'])
        form = BankbookCreateForm(instance=instance)
        context = {'form': form, 'update': True, 'bankbook': Flat.objects.get(id=instance.flat_id)}
        return context

    def post(self, request, *args, **kwargs):
        instance = BankBook.objects.get(id=self.kwargs['pk'])
        form = BankbookCreateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('/admin_app/bankbook_list')


def delete_bankbook(request, bankbook_id):
    BankBook.objects.get(id=bankbook_id).delete()
    return redirect('/admin_app/bankbook_list')


class BankbookDetail(DetailView):
    model = BankBook
    template_name = 'admin_app/bank_book/detail.html'


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
    pass
def get_bankbooks(request):
    if is_ajax(request):
        bankbooks = BankBook.objects.filter(flat__owner_id=request.GET.get('owner')).values('id')
        return JsonResponse(json.dumps({'bankbooks': list(bankbooks)}), safe=False)


class ReceiptList(ListView):
    pass



class CreateReceipt(CreateView):
    pass


