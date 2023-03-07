from django import forms
from my_store_app.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class AuthorRegisterForm(forms.Form):
    full_name = forms.CharField(required=True, help_text='имя пользователя')
    phone = forms.CharField(required=True, help_text='номер телефона')
    email = forms.EmailField(required=True,  help_text='email')
    login = forms.CharField(required=True, help_text='логин')
    password = forms.CharField(required=True, help_text='пароль')


