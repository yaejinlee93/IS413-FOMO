from django_mako_plus import view_function
from django.http import HttpResponseRedirect
from django import forms
from formlib.form import Formless
from catalog import models as cmod
import re

@view_function
def process_request(request):
    #process the form_method
    form = CreateForm(request)

    if form.is_valid():
        form.commit()
        return HttpResponseRedirect('/manager/product')

    #render the form
    context = {
        'form': form,
    }
    return request.dmp_render('create.html', context)

class CreateForm(Formless):
    def init(self):
        self.fields['type'] = forms.ChoiceField(label='Product Type', choices = cmod.Product.TYPE_CHOICES)
        #self.fields['status'] = forms.ChoiceField(label='Status')
        self.fields['name'] = forms.CharField(label='Name')
        self.fields['description'] = forms.CharField(label='Description')
        self.fields['category'] = forms.ModelChoiceField(label='Category', queryset=cmod.Category.objects.all())
        self.fields['price'] = forms.DecimalField(label='Price')
        self.fields['quantity'] = forms.IntegerField(label='Quantity', required=False)
        self.fields['quantity'].widget.attrs = { 'class':'BulkProduct' }
        self.fields['reorder_trigger'] = forms.IntegerField(label='Reorder Trigger', required=False)
        self.fields['reorder_trigger'].widget.attrs = { 'class':'BulkProduct' }
        self.fields['reorder_quantity'] = forms.IntegerField(label='Reorder Quantity', required=False)
        self.fields['reorder_quantity'].widget.attrs = { 'class':'BulkProduct' }
        self.fields['itemID'] = forms.CharField(label='Item ID', required=False)
        self.fields['itemID'].widget.attrs = { 'class':'IndividualProduct RentalProduct' }
        self.fields['max_rental_days'] = forms.IntegerField(label='Maximum Rental Days', required=False)
        self.fields['max_rental_days'].widget.attrs = { 'class':'RentalProduct' }
        self.fields['retire_date'] = forms.DateField(label='Retire Date', required=False)
        self.fields['retire_date'].widget.attrs = { 'class':'RentalProduct' }

    def clean(self):

        if self.cleaned_data.get('type') == 'BulkProduct':
            if self.cleaned_data.get('quantity') is None:
                raise forms.ValidationError('Quantity is required.')
            if self.cleaned_data.get('reorder_trigger') is None:
                raise forms.ValidationError('Reorder Trigger is required.')
            if self.cleaned_data.get('reorder_quantity') is None:
                raise forms.ValidationError('Reorder Quantity is required.')

        elif self.cleaned_data.get('type') == 'IndividualProduct':
            if self.cleaned_data.get('itemID') is None:
                raise forms.ValidationError('Item ID is required.')

        elif self.cleaned_data.get('type') == 'RentalProduct':
            if self.cleaned_data.get('itemID') is None:
                raise forms.ValidationError('Item ID is required.')
            if self.cleaned_data.get('max_rental_days') is None:
                raise forms.ValidationError('Maximum Remtal Days is required.')
            if self.cleaned_data.get('retire_date') is None:
                raise forms.ValidationError('Retire Date is required.')

        return self.cleaned_data

    def commit(self):

        if self.cleaned_data.get('type') == 'BulkProduct':
            product = cmod.BulkProduct()
            product.category = self.cleaned_data.get('category')
            product.type = self.cleaned_data.get('type')
            product.name = self.cleaned_data.get('name')
            product.description = self.cleaned_data.get('description')
            product.price = self.cleaned_data.get('price')
            product.quantity = self.cleaned_data.get('quantity')
            product.reorder_trigger = self.cleaned_data.get('reorder_trigger')
            product.reorder_quantity = self.cleaned_data.get('reorder_quantity')

        elif self.cleaned_data.get('type') == 'IndividualProduct':
            product = cmod.IndividualProduct()
            product.category = self.cleaned_data.get('category')
            product.type = self.cleaned_data.get('type')
            product.name = self.cleaned_data.get('name')
            product.description = self.cleaned_data.get('description')
            product.price = self.cleaned_data.get('price')
            product.itmeID = self.cleaned_data.get('itmeID')

        elif self.cleaned_data.get('type') =='RentalProduct':
            product = cmod.RentalProduct()
            product.category = self.cleaned_data.get('category')
            product.type = self.cleaned_data.get('type')
            product.name = self.cleaned_data.get('name')
            product.description = self.cleaned_data.get('description')
            product.price = self.cleaned_data.get('price')
            product.itmeID = self.cleaned_data.get('itmeID')
            product.max_rental_days = self.cleaned_data.get('max_rental_days')
            product.retire_date = self.cleaned_data.get('retire_date')

        product.save()
