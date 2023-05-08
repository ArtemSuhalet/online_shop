from django import forms
from django.core.validators import RegexValidator
from my_store_app.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _



class AuthForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class AuthorRegisterForm(forms.Form):
    full_name = forms.CharField(required=True, help_text='имя пользователя')
    phone_valid = RegexValidator(regex=r'^\+?1?\d{6,15}$',
                                 message=' '.join([str(_('номер телефона необходимо вводить в формате:')), '+999999999',
                                                   str(_('до 15 символов.'))]))
    phone = forms.CharField(required=True, validators=[phone_valid], help_text='номер телефона')
    email = forms.EmailField(required=True,  help_text='email')
    login = forms.CharField(required=True, help_text='логин')
    password = forms.CharField(required=True, help_text='пароль')

class AccountEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'username', 'password')



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ['product', 'user', 'author', 'content', 'rating']



#===================================Формы для корзины===============================


class CartAddProductForm(forms.Form):
    """Form for adding product to cart"""
    quantity = forms.IntegerField(min_value=1)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class OrderStepOneForm(forms.ModelForm):
    """
    Order progress first step form. Adding name, surname, phone and email
    to order information.
    """
    class Meta:
        model = Order
        fields = ['fio', 'phone', 'email']


class OrderStepTwoForm(forms.ModelForm):
    """
    Order progress second step form. Adding delivery type, city and address
    to order information.
    """
    class Meta:
        model = Order
        widgets = {
            'delivery': forms.RadioSelect(
                attrs={
                    'class': 'toggle-box'
                }
            ),
            'address': forms.Textarea(
                attrs={
                    'class': 'form-textarea'
                }
            )
        }
        fields = ['delivery', 'city', 'address']


class OrderStepThreeForm(forms.ModelForm):
    """
    Order progress third step form. Adding payment method
    to order information.
    """
    class Meta:
        model = Order
        widgets = {
            'payment_method': forms.RadioSelect(
                attrs={
                    'class': 'toggle-box'
                }
            ), }
        fields = ['payment_method']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['number']



class SortForm(forms.Form):
    sort_form = forms.TypedChoiceField(label='sort of',choices=[('pop', 'популярности'), ('price', 'цене'), ('name', 'имени'),('review', 'отзывам')])