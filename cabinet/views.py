from django.contrib.auth import login, authenticate
from wkhtmltopdf.views import PDFTemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.edit import FormMixin, CreateView
from xhtml2pdf import pisa
from account.forms import *
from account.models import *
from admin_app.forms import ReceiptFilterForm, MasterRequestForm
from admin_app.models import Flat, Receipt, Message, logger, MasterRequest
from admin_app.views import FilterMixin
from myhouse import settings


# Create your views here.

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


def index(request):
    if request.GET.get('admin'):
        owner_cabinet = OwnerCabinet(request)
        owner_cabinet.set_admin(request.GET.get('admin'))
    return render(request, 'cabinet/index.html')


class Summary(DetailView):
    model = Flat
    template_name = 'cabinet/summary.html'

    def get_context_data(self, **kwargs):
        flat = Flat.objects.get(id=self.kwargs['pk'])
        context = {'flat': flat}
        return context


class ReceiptList(FormMixin, FilterMixin, ListView):
    model = Receipt
    form_class = ReceiptFilterForm
    template_name = 'cabinet/receipt/index.html'

    def get_context_data(self, **kwargs):
        flat = Flat.objects.get(owner_id=self.request.user.id)
        receipt_list = Receipt.objects.filter(flat_id=flat.id)

        return {'receipt_list': receipt_list, 'form': ReceiptFilterForm()}

    def get_form_kwargs(self, *args, **kwargs):
        # use GET parameters as the data
        kwargs = super().get_form_kwargs(*args, **kwargs)
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs


class ReceiptDetail(DetailView):
    model = Receipt
    template_name = 'cabinet/receipt/detail.html'


class FlatServiceDetail(DetailView):
    model = Flat
    template_name = 'cabinet/tariff/index.html'


class MessageList(ListView):
    model = Message
    template_name = 'cabinet/message/index.html'

    def get_context_data(self, **kwargs):
        context = {'message_list': Message.objects.filter(owner_id=self.request.user.id)}
        return context


class MessageDetail(DetailView):
    model = Message
    template_name = 'cabinet/message/detail.html'


def delete_message(request):
    logger.info(request.POST)
    Message.objects.filter(id__in=request.POST.getlist('ids[]')).delete()
    return redirect('/cabinet/message_list')


class MasterRequestList(ListView):
    model = MasterRequest
    template_name = 'cabinet/master_request/index.html'
    ordering = ['-id']

    def get_queryset(self):
        qs = super(MasterRequestList, self).get_queryset()
        user = User.objects.get(id=self.request.user.id)
        qs = qs.filter(flat__owner=user.owner)
        return qs


class MasterRequestCreate(CreateView):
    model = MasterRequest
    template_name = 'cabinet/master_request/create.html'
    form_class = MasterRequestForm
    success_url = reverse_lazy('cabinet:master_request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        owner = Owner.objects.get(user_id=self.request.user.id)
        context['owner'] = owner.user_id
        return context

    
def delete_master_request(request, pk):
    MasterRequest.objects.get(id=pk).delete()
    return redirect('cabinet:master_request_list')


class OwnerProfile(LoginRequiredMixin, View):

    def get(self, request):
        owner = Owner.objects.get(user_id=request.user.id)
        return render(request, 'cabinet/owner/index.html', {'owner': owner})


class UpdateOwner(UpdateView):
    model = Owner
    template_name = 'cabinet/owner/update.html'

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
        if 'password' in user_form.changed_data:
            psw = user_form.cleaned_data['password']
            created_user.set_password(user_form.cleaned_data['password'])
        created_user.save()
        owner_form.save()
        email = user_form.cleaned_data['email']
        user = authenticate(self.request, username=email, password=user_form.cleaned_data['password'])
        login(self.request, user)
        return redirect('/cabinet/owner_profile')

    def form_invalid(self, user_form, owner_form):
        """If the form is invalid, render the invalid form."""
        context = {
            'owner_form': owner_form,
            'user_form': user_form
        }
        return self.render_to_response(context)


def render_pdf_view(request, receipt_id):
    template_path = 'cabinet/receipt/pdf.html'
    requisites = PaymentDetails.objects.first()
    receipt = Receipt.objects.get(id=receipt_id)
    # print(receipt.flat.owner.user.first_name)
    print(settings.STATIC_URL)
    context = {'requisites': requisites.description,
               'static': settings.STATIC_URL,
               'receipt': receipt}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
       html.encode('UTF-8'), dest=response, encoding='utf-8')
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


class MyPDF(PDFTemplateView):
    filename = 'my_pdf.pdf'
    template_name = '/cabinet/receipt/pdf.html'
    cmd_options = {
        'margin-top': 3,
    }

    def get_context_data(self, **kwargs):
        context = super(MyPDF, self).get_context_data(**kwargs)
        requisites = PaymentDetails.objects.first()
        context['requisites'] = requisites.information
        return context