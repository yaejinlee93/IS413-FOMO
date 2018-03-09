from django_mako_plus import view_function
from django.http import HttpResponseRedirect
from django import forms
from formlib.form import Formless
from catalog import models as cmod
from django.forms.models import model_to_dict
import re

def set_product_title(x):
    global product_title
    product_title = x

def print_product_title():
    return product_title

@view_function
def process_request(request, product: cmod.Product):
    #process the form_method

    set_product_title(product.TITLE)

    data = model_to_dict(product)
    #data['type'] = product.__class__.__name__
    #product = cmod.Product.objects.get(id=request.urlparams[0])

    form = EditForm(request, initial = data)

    if form.is_valid():
        form.commit(product)
        return HttpResponseRedirect('/manager/product')

    #render the form
    context = {
        'form': form,
    }
    return request.dmp.render('edit.html', context)

class EditForm(Formless):
    def init(self):

        pruduct_title = print_product_title()

        self.fields['name'] = forms.CharField(label='Name')
        self.fields['description'] = forms.CharField(label='Description')
        #self.fields['status'] = forms.ChoiceField(label='Status', choices = cmod.Product.STATUS_CHOICES)
        self.fields['category'] = forms.ModelChoiceField(label='Category', queryset=cmod.Category.objects.all())
        self.fields['price'] = forms.DecimalField(label='Price')

        if product_title == "Bulk":
            self.fields['quantity'] = forms.IntegerField(label='Quantity', required=False)
            self.fields['reorder_trigger'] = forms.IntegerField(label='Reorder Trigger', required=False)
            self.fields['reorder_quantity'] = forms.IntegerField(label='Reorder Quantity', required=False)

        elif product_title == "Individual":
            self.fields['itemID'] = forms.CharField(label='Item ID', required=False)

        elif product_title == "Rental":
            self.fields['itemID'] = forms.CharField(label='Item ID', required=False)
            self.fields['max_rental_days'] = forms.IntegerField(label='Maximum Rental Days', required=False)
            self.fields['retire_date'] = forms.DateField(label='Retire Date', required=False)

    def clean(self):

        pruduct_title = print_product_title()

        if product_title == "Bulk":
            if self.cleaned_data.get('quantity') is None:
                raise forms.ValidationError('Quantity is required.')
            if self.cleaned_data.get('reorder_trigger') is None:
                raise forms.ValidationError('Reorder Trigger is required.')
            if self.cleaned_data.get('reorder_quantity') is None:
                raise forms.ValidationError('Reorder Quantity is required.')

        elif product_title == "Individual":
            if self.cleaned_data.get('itemID') is None:
                raise forms.ValidationError('Item ID is required.')

        elif product_title == "Rental":
            if self.cleaned_data.get('itemID') is None:
                raise forms.ValidationError('Item ID is required.')
            if self.cleaned_data.get('max_rental_days') is None:
                raise forms.ValidationError('Maximum Remtal Days is required.')
            if self.cleaned_data.get('retire_date') is None:
                raise forms.ValidationError('Retire Date is required.')

        return self.cleaned_data

    def commit(self, product):

        pruduct_title = print_product_title()

        p = product

        if product_title == "Bulk":

            p.category = self.cleaned_data.get('category')
            p.type = self.cleaned_data.get('type')
            p.name = self.cleaned_data.get('name')
            product.description = self.cleaned_data.get('description')
            p.price = self.cleaned_data.get('price')
            p.quantity = self.cleaned_data.get('quantity')
            p.reorder_trigger = self.cleaned_data.get('reorder_trigger')
            p.reorder_quantity = self.cleaned_data.get('reorder_quantity')

        elif product_title == "Individual":

            product.category = self.cleaned_data.get('category')
            product.type = self.cleaned_data.get('type')
            product.name = self.cleaned_data.get('name')
            product.description = self.cleaned_data.get('description')
            product.price = self.cleaned_data.get('price')
            product.itmeID = self.cleaned_data.get('itmeID')

        elif product_title == "Rental":

            product = cmod.RentalProduct()
            product.category = self.cleaned_data.get('category')
            product.type = self.cleaned_data.get('type')
            product.name = self.cleaned_data.get('name')
            product.description = self.cleaned_data.get('description')
            product.price = self.cleaned_data.get('price')
            product.itmeID = self.cleaned_data.get('itmeID')
            product.max_rental_days = self.cleaned_data.get('max_rental_days')
            product.retire_date = self.cleaned_data.get('retire_date')

        p.save()
