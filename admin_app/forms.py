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
