from django import forms
from admin_app.models import *
from my_store_app.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _



class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'


class MultiFileForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = File


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        template_name = 'create_product.html'
        fields = '__all__'
