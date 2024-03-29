import math

from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from admin_app.models import *


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = '__all__'

    def clean(self):
        try:
            name = self.cleaned_data['name']
        except ValueError:
            raise forms.ValidationError('Данная единица измерения уже существует')

        return self.cleaned_data


class ServiceForm(forms.ModelForm):
    unit = forms.ModelChoiceField(label='Едм. изм.', queryset=Unit.objects.all(), empty_label='Выберите...', required=False)

    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'show': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }

    def clean(self):
        try:
            name = self.cleaned_data['name']
        except ValueError:
            raise forms.ValidationError('Данный сервис уже существует')

        return self.cleaned_data


class TariffServiceForm(forms.ModelForm):
    unit = forms.ModelChoiceField(queryset=Unit.objects.all(), empty_label='Выберите...', required=False, disabled=True)
    service = forms.ModelChoiceField(queryset=Service.objects.all(), empty_label='Выберите...')

    class Meta:
        model = TariffService
        fields = '__all__'
        widgets = {
            'currency': forms.TextInput(attrs={'readonly': 'readonly', 'value': 'грн'}),
        }


class TariffCreateForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = '__all__'


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = '__all__'


class PaymentDetailsForm(forms.ModelForm):
    class Meta:
        model = PaymentDetails
        fields = '__all__'


class PaymentItemsForm(forms.ModelForm):
    class Meta:
        model = PaymentItems
        fields = '__all__'


class MainPageForm(forms.ModelForm):
    class Meta:
        model = MainPage
        exclude = ['seo']


class SlideForm(forms.ModelForm):
    class Meta:
        model = Slide
        fields = '__all__'
        widget = {
            'image': forms.FileInput(attrs={
                'type': 'file',
                'name': 'files[]',
                'class': 'imageInput',
                'accept': '.jpg, .img, .png, .gif',
                'style': 'display: none'}),
        }


class SeoCreateForm(forms.ModelForm):
    class Meta:
        model = SeoText
        fields = '__all__'


class NearBlockForm(forms.ModelForm):

    class Meta:
        model = NearBlock
        fields = '__all__'


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        exclude = ['seo']


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = '__all__'


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'name']
        widget = {
            'file': forms.FileInput(attrs={
                'type': 'file',
                'name': 'files[]',
                'accept': '.jpg, .pdf'}),
        }


class ServiceBlockForm(forms.ModelForm):
    class Meta:
        model = ServicePage
        fields = '__all__'


class ContactPageForm(forms.ModelForm):
    class Meta:
        model = ContactPage
        exclude = ['seo']


class InviteForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ['phone', 'mail']
        widget = {
            'phone': forms.TextInput(attrs={'data-mask': "(000)-000-00-00", 'placeholder': '(000)-000-00-00'}),
        }


class HouseFilterForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


class SectionForm(forms.ModelForm):

    class Meta:
        model = Section
        exclude = ['house']


class LevelForm(forms.ModelForm):

    class Meta:
        model = Level
        exclude = ['house']


class HouseUserForm(forms.ModelForm):
    profile = forms.ModelChoiceField(
        label='ФИО',
        queryset=Profile.objects.all(), empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = House.users.through
        fields = ['profile']


class HouseCreateForm(forms.ModelForm):
    image1 = forms.ImageField(required=False, error_messages={'invalid': "Только изображения"}, widget=forms.FileInput,
                              label="Изображение #1. Размер: (522x350)")
    image2 = forms.ImageField(required=False, error_messages={'invalid': "Только изображения"}, widget=forms.FileInput,
                              label="Изображение #2. Размер: (248x160)")
    image3 = forms.ImageField(required=False, error_messages={'invalid': "Только изображения"}, widget=forms.FileInput,
                              label="Изображение #3. Размер: (248x160)")
    image4 = forms.ImageField(required=False, error_messages={'invalid': "Только изображения"}, widget=forms.FileInput,
                              label="Изображение #4. Размер: (248x160)")
    image5 = forms.ImageField(required=False, error_messages={'invalid': "Только изображения"}, widget=forms.FileInput,
                              label="Изображение #5. Размер: (248x160)")

    class Meta:
        model = House
        exclude = ['users']


class FlatFilterForm(forms.Form):
    number = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'data-number': '1'}))
    house = forms.ModelChoiceField(queryset=House.objects.all(), empty_label='',
                                   widget=forms.Select(attrs={'class': 'form-control', 'data-number': '2'}))
    section = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control', 'data-number': '3'}))
    level = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control', 'data-number': '4'}))
    owner = forms.ModelChoiceField(queryset=Owner.objects.all(), empty_label='',
                                   widget=forms.Select(attrs={'class': 'form-control', 'data-number': '5'}))


class FlatCreateForm(forms.ModelForm):
    house = forms.ModelChoiceField(
        label='Дом',
        queryset=House.objects.all(), empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    section = forms.ModelChoiceField(
        required=False,
        queryset=Section.objects.all(),
        label='Секция',
        empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    level = forms.ModelChoiceField(
        required=False,
        queryset=Level.objects.all(),
        label='Этаж',
        empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    owner = forms.ModelChoiceField(
        required=False,
        queryset=Owner.objects.all(),
        label='Владелец',
        empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    bank_book = forms.ModelChoiceField(
        required=False,
        queryset=BankBook.objects.filter(status='Активен', flat_id=None),
        label='Лицевой счет',
        empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Flat
        fields = '__all__'


class CounterFilterForm(forms.Form):
    try:
        flat__house = [(f'{x.id}', f'{x.name}') for x in House.objects.all()]
        services = [(f'{x.id}', f'{x.name}') for x in Service.objects.all()]
        sections = [(f'{x.id}', f'{x.name}') for x in Section.objects.all()]
    except:
        flat__house = ['']
        services = ['']
        sections = ['']
    flat__house.insert(0, ('', ''))
    services.insert(0, ('', ''))
    sections.insert(0, ('', ''))
    flat__house_id = forms.ChoiceField(choices=flat__house, widget=forms.Select(attrs={'class': 'form-control', 'data-number': '1'}))
    section = forms.ChoiceField(choices=sections, widget=forms.Select(attrs={'class': 'form-control', 'data-number': '2'}))
    flat__number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-number': '3'}))
    service = forms.ChoiceField(choices=services, widget=forms.Select(attrs={'class': 'form-control', 'data-number': '4'}))


class CounterCreateForm(forms.ModelForm):
    house = forms.ModelChoiceField(
        label='Дом',
        queryset=House.objects.all(), empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    section = forms.ModelChoiceField(
        required=False,
        queryset=Section.objects.all(),
        label='Секция',
        empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Counter
        fields = '__all__'


class FlatCounterFilterForm(CounterFilterForm):
    try:
        flat__house = [(f'{x.id}', f'{x.name}') for x in House.objects.all()]
    except:
        flat__house = ['']
    flat__house_id = forms.ChoiceField(choices=flat__house,
                                       widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_flat__house_id'}))
    section = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_section'}))
    id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-number': '5'}))
    flat__number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_flat__number'}))
    status = forms.ChoiceField(choices=Counter.TypesCounter.choices, widget=forms.Select(
        attrs={'class': 'form-control', 'data-number': '6'}))
    date = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-number': '7'}))


class CashBoxFilterForm(forms.Form):
    try:
        payment_type = [(f'{x.name}', f'{x.name}') for x in PaymentItems.objects.all()]
        bankbook__flat__owner = [(f'{x}', f'{x}') for x in Owner.objects.all()]
    except:
        payment_type = ['']
        bankbook__flat__owner = ['']

    payment_type.insert(0, ('', ''))
    bankbook__flat__owner.insert(0, ('', ''))
    bankbook__flat__owner.insert(1, ('(не задано)', '(не задано)'))
    id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_range = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    status = forms.ChoiceField(choices=(('', ''), ('Проведен', 'Проведен'), ('Не проведен', 'Не проведен')),
                               widget=forms.Select(attrs={'class': 'form-control'}))
    payment_type_id =forms.ChoiceField(choices=payment_type, widget=forms.Select(attrs={'class': 'form-control'}))

    bankbook__flat__owner_id = forms.ChoiceField(choices=bankbook__flat__owner, widget=forms.Select(attrs={'class': 'form-control'}))

    bankbook_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    type = forms.ChoiceField(choices=CashBox.Types.choices, widget=forms.Select(attrs={'class': 'form-control'}))


class CashBoxIncomeCreateForm(forms.ModelForm):
    owner = forms.ModelChoiceField(
        required=False,
        label='Владелец',
        queryset=Owner.objects.all(), empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    payment_type = forms.ModelChoiceField(
        label='Тип платежа', queryset=PaymentItems.objects.filter(status='Приход'),
        required=False, empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CashBox
        fields = '__all__'
        widgets = {
            "type": forms.HiddenInput(attrs={
                'value': 'приход'
            })
        }


class CashBoxExpenseCreateForm(forms.ModelForm):
    payment_type = forms.ModelChoiceField(
        label='Тип платежа', queryset=PaymentItems.objects.filter(status='Расход'),
        required=False, empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CashBox
        exclude = ['bankbook']
        widgets = {
            "type": forms.HiddenInput(attrs={
                'value': 'расход'
            })
        }

    def clean_amount_of_money(self):
        return math.fabs(self.cleaned_data['amount_of_money'])


class BankBookFilterForm(forms.Form):
    try:
        flat__house = [(f'{x.id}', f'{x.name}') for x in House.objects.all()]

        flat__owner = [(f'{x}', f'{x}') for x in Owner.objects.all()]
    except:
        flat__house = ['']
        flat__owner = ['']

    flat__house.insert(0, ('', ''))

    flat__owner.insert(0, ('', ''))
    id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'bb_id'}))
    status = forms.ChoiceField(choices=BankBook.Status.choices, widget=forms.Select(attrs={'class': 'form-control',
                                                                                           'data-number': '2', 'id': 'status'}))
    flat__house_id = forms.ChoiceField(choices=flat__house, widget=forms.Select(attrs={'class': 'form-control' , 'id': 'house'}))
    section = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control', 'id': 'section'}))
    flat__number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'flat'}))
    flat__owner_id = forms.ChoiceField(choices=flat__owner, widget=forms.Select(attrs={'class': 'form-control', 'id': 'owner'}))
    balance = forms.ChoiceField(choices=((' ', ' '), ('Есть долг', 'Есть долг'), ('Нет долга', 'Нет долга')),
                                       widget=forms.Select(attrs={'class': 'form-control', 'id': 'balance'}))


class BankbookCreateForm(forms.ModelForm):
    house = forms.ModelChoiceField(
        label='Дом', required=False,
        queryset=House.objects.all(), empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    section = forms.ModelChoiceField(
        required=False,
        queryset=Section.objects.all(),
        label='Секция',
        empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = BankBook
        fields = '__all__'


class ReceiptFilterForm(forms.Form):
    try:
        flat__owner = [(f'{x}', f'{x}') for x in Owner.objects.all()]
    except:
        flat__owner = ['']

    flat__owner.insert(0, ('', ''))
    id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    status = forms.ChoiceField(choices=Receipt.Status.choices,
                               widget=forms.Select(attrs={'class': 'form-control'}))
    date_range = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    flat__number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    flat__owner_id = forms.ChoiceField(choices=flat__owner, widget=forms.Select(attrs={'class': 'owner_select form-control', 'name': "states[]"}))
    is_checked = forms.ChoiceField(choices=(('', ''), (True, 'Проведена'), (False, 'Не проведена')),
                                   widget=forms.Select(attrs={'class': 'form-control'}))


class ReceiptCreateForm(forms.ModelForm):
    house = forms.ModelChoiceField(
        label='Дом',
        queryset=House.objects.all(), empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    section = forms.ModelChoiceField(
        required=False,
        queryset=Section.objects.all(),
        label='Секция',
        empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    bankbook = forms.CharField(label='Лицевой счет', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Receipt
        exclude = ['services']


class ReceiptServiceForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        required=False,
        queryset=Service.objects.all(),
        label='Услуга',
        empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ReceiptService
        fields = '__all__'


class MasterRequestFilterForm(forms.Form):
    try:
        flat__owner = [(f'{x}', f'{x}') for x in Owner.objects.all()]
        master = [(f'{x}', f'{x}') for x in Profile.objects.all()]
    except:
        flat__owner = ['']
        master = ['']
    flat__owner.insert(0, ('', ''))
    master.insert(0, ('', ''))
    id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_range = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    type = forms.ChoiceField(choices=MasterRequest.TypeMaster.choices,
                             widget=forms.Select(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    flat__number = forms.CharField(max_length=20, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    flat__owner_id = forms.ChoiceField(choices=flat__owner, widget=forms.Select(attrs={'class': 'form-control'}))
    flat__owner_phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))

    master_id = forms.ChoiceField(choices=master, widget=forms.Select(attrs={'class': 'form-control'}))
    status = forms.ChoiceField(choices=MasterRequest.Status.choices,
                               widget=forms.Select(attrs={'class': 'form-control'}))


class FlatModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.number + ', ' + obj.house.name


class MasterRequestForm(forms.ModelForm):
    owner = forms.ModelChoiceField(
        required=False,
        label='Владелец',
        queryset=Owner.objects.all(), empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}))
    flat = FlatModelChoiceField(
        label='Квартира',
        queryset=Flat.objects.all(), empty_label='Выберите...',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = MasterRequest
        fields = '__all__'


class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        exclude = ['from_user']


class ReceiptTemplateForm(forms.ModelForm):

    class Meta:
        model = Template
        exclude = ('is_default',)



ServiceFormset = modelformset_factory(model=Service, form=ServiceForm, extra=0)
UnitFormset = modelformset_factory(model=Unit, form=UnitForm, extra=0)
TariffServiceFormSet = modelformset_factory(model=TariffService, form=TariffServiceForm, extra=0)
RoleFormSet = modelformset_factory(model=Role, form=RoleForm, extra=0)
SlideFormSet = modelformset_factory(model=Slide, form=SlideForm, extra=0)
NearBlockFormSet = modelformset_factory(model=NearBlock, form=NearBlockForm, extra=0)
GalleryFormSet = modelformset_factory(model=Gallery, form=GalleryForm, extra=0)
ExtraGalleryFormSet = modelformset_factory(model=Gallery, form=GalleryForm, extra=0)
DocumentFormSet = modelformset_factory(model=Document, form=DocumentForm, extra=0)
ServiceBlockFormSet = modelformset_factory(model=ServiceBlock, form=ServiceBlockForm, extra=0)
SectionFormSet = inlineformset_factory(House, Section, form=SectionForm, extra=0)
LevelFormSet = inlineformset_factory(House, Level, form=LevelForm, extra=0)
HouseUserFormSet = inlineformset_factory(House, House.users.through, form=HouseUserForm, extra=0)
ReceiptServiceFormSet = inlineformset_factory(Receipt, ReceiptService, form=ReceiptServiceForm, extra=0, can_delete=True)