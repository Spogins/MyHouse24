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


ServiceFormset = modelformset_factory(model=Service, form=ServiceForm, extra=0)
UnitFormset = modelformset_factory(model=Unit, form=UnitForm, extra=0)
TariffServiceFormSet = modelformset_factory(model=TariffService, form=TariffServiceForm, extra=0)
RoleFormSet = modelformset_factory(model=Role, form=RoleForm, extra=0)