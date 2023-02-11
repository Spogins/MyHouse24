from django.contrib.auth.models import User
from django import forms

from account.models import *


class ProfileChangeForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['phone', 'role', 'status']
        widgets = {
            'phone': forms.TextInput(attrs={'data-mask': "(000)-000-00-00",
                                            'placeholder': '(000)-000-00-00'}),
        }


class UserChangeForm(forms.ModelForm):
    confirm_password = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput, required=False)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=False)
    email = forms.EmailField(required=True, label='Адрес электроннной почты')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.id:
            self.fields['password'] = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)
            self.fields['confirm_password'] = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)

    def clean(self):
        try:
            password = self.cleaned_data['password']
            confirm_password = self.cleaned_data['confirm_password']
        except KeyError:
            raise forms.ValidationError('Введите пароли')
        if 'password' in self.changed_data:
            if password != confirm_password:
                raise forms.ValidationError(f'Пароли не совпадают')
        return self.cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if 'email' in self.changed_data:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(f'Данный почтовый адрес уже зарегистрирован в системе')
        return email

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password']


class LoginForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'E-mail'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'Пользователь с email {email} не найден.')
        user = User.objects.filter(email=email).first()
        if user:
            if not user.check_password(password):
                raise forms.ValidationError("Неверный пароль")
        if not Profile.objects.filter(user_id=user.id).exists():
            raise forms.ValidationError('Пользователя не найдено')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'E-mail или ID'
            })
        }


class LoginOwnerForm(LoginForm):

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'Пользователь с email {email} не найден.')
        user = User.objects.filter(email=email).first()
        if user:
            if not user.check_password(password):
                raise forms.ValidationError("Неверный пароль")
        if not Owner.objects.filter(user_id=user.id).exists():
            raise forms.ValidationError('Пользователя не найдено')
        return self.cleaned_data


