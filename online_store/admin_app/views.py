import datetime
from admin_app.forms import *
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.utils.formats import date_format
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from my_store_app.models import *
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from admin_app.models import *

def admin_view(request):
    # items = Product.objects.all()
    # categories = ProductCategory.objects.all()
    # orders = Order.objects.all()
    # reviews = ProductComment.objects.all()
    # render(request, 'admin_list.html', {'categories': categories,
    #                                     'items': items,
    #                                     'orders': orders,
    #                                     'reviews': reviews,
    #                                     })
    time = _('Сейчас - %(date)s %(time)s') % {
        'date': date_format(datetime.datetime.now().date(), format='SHORT_DATE_FORMAT', use_l10n=True),
        'time': datetime.datetime.now().time().replace(microsecond=0)
    }
    return render(request, 'admin_list.html', context={'time': time})


class ItemsListView(ListView):
    model = Product
    template_name = 'items_list.html'
    context_object_name = 'items_list'
    paginate_by = 4


class ItemDetailView(DetailView):
    model = Product
    template_name = 'item_detail.html'


class ItemCreateView(PermissionRequiredMixin, CreateView):

    def has_permission(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied
        return True

    def get(self, request, *args, **kwargs):
        context = {'form': ProductCreateForm()}
        return render(request, 'create_item.html', context)

    def post(self, request, *args, **kwargs):
        form = ProductCreateForm(request.POST)
        if form.is_valid():
            Product.objects.create(**form.cleaned_data)
            return redirect('admin_app:item_list')
        return render(request, 'create_item.html', context={'form': form})




class ItemEditFormView(View):
    model = SingletonModel
    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        product_form = ProductForm(instance=product)
        return render(request, 'edit_product.html', context={'product_form': product_form, 'product_id': product_id})

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        product_form = ProductForm(request.POST, instance=product)
        product_id = product.id
        if product_form.is_valid():
            product.save()
            return redirect('admin_app:item_detail', product_id)
        return render(request, 'edit_product.html', context={'product_form': product_form, 'product_id': product_id})

def upload_files(request):
    if request.method == 'POST':
        form = MultiFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('file_field')
            for f in files:
                instance = File(file=f)
                instance.save()
            return redirect('admin_app:admin_list')
    else:
        form = MultiFileForm()
    return render(request, 'upload.html', {'form': form})




class CategoriesListView(ListView):
    model = ProductCategory
    template_name = 'categories_list.html'
    context_object_name = 'categories_list'

class OrdersListView(ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'order_list'


class ReviewsListView(ListView):
    model = ProductComment
    template_name = 'reviews_list.html'
    context_object_name = 'reviews_list'

class UsersListView(ListView):
    model = User
    template_name = 'users_list.html'
    context_object_name = 'users_list'