from django.contrib.auth.models import User
from django import forms

from account.models import *
from admin_app.models import *


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

    def clean_password(self):
        password = self.cleaned_data['password']
        if password:
            return password
        else:
            return None

    def clean(self):
        try:
            if self.cleaned_data['password'] != '' and self.cleaned_data['confirm_password'] != '':
                password = self.cleaned_data['password']
                confirm_password = self.cleaned_data['confirm_password']
            else:
                raise forms.ValidationError('Введите пароли')
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


class OwnerFilterForm(forms.Form):
    id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-number': '1', 'id': 'owner_id'}))
    fullname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-number': '2', 'id': 'fullname'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-number': '3', 'id': 'phone'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-number': '4', 'id': 'email'}))
    house = forms.ModelChoiceField(queryset=House.objects.all(), empty_label='',
                                   widget=forms.Select(attrs={'class': 'form-control', 'data-number': '5', 'id': 'house'}))
    flat = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-number': '6', 'id': 'flat'}))
    date = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'data-number': '7', 'id': 'date'}))
    status = forms.ChoiceField(choices=(('', ''), ('Активен', 'Активен'), ('Новый', 'Новый'), ('Отключен', 'Отключен')),
                               widget=forms.Select(attrs={'class': 'form-control', 'data-number': '8', 'id': 'status'}))
    debt = forms.ChoiceField(choices=(('', ''), ('Да', 'Да')),
                             widget=forms.Select(attrs={'class': 'form-control', 'data-number': '9', 'id': 'debt'}))


class OwnerChangeForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, error_messages={'invalid': "Только изображения"}, widget=forms.FileInput,
                              label="Сменить изображения")

    class Meta:
        model = Owner
        exclude = ['user', 'created']
        widgets = {
            'phone': forms.TextInput(attrs={'data-mask': "(000)-000-00-00",
                                            'placeholder': '(000)-000-00-00'}),
        }