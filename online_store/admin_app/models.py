from django.http import HttpResponseRedirect
from django.shortcuts import render
#from admin_app.forms import ModelFormWithFileField
from django.db import models


class File(models.Model):
    file = models.FileField(upload_to='static/')
