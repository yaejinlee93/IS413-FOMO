from django.conf import settings
from django_mako_plus import view_function, jscontext
from datetime import datetime, timezone, timedelta
from account import models as amod
from catalog import models as cmod
from formlib import Formless
from django import forms
import random
import string
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required
@view_function
def process_request(request, path=''):
    #utc_time = datetime.utcnow()
    order = request.user.get_shopping_cart()
    Formless.submit_text = None
    form = MyForm(request)
    if form.is_valid():
        form.commit()
        return HttpResponseRedirect('/catalog/receipt/'+ str(order.id))

    #recaluclate the order before displaying the form
    order.recalculate()
    # tax_product = cmod.Product.objects.get(name='TaxAmount')
    # tax_item = order.get_item(tax_product)
    total_price = order.total_price
    stripe_price = int(total_price * 100)

    context = {
        # list of categories
        'form': form,
        'total_price': total_price,
        'stripe_price': stripe_price,
    }
    return request.dmp.render('checkout.html', context)

class MyForm(Formless):
    '''Checkout Form'''
    def init(self):
        '''Adds the fields for this form'''
        #SHIPPING FIELDS
        self.fields['name'] = forms.CharField(label='Ship to')
        self.fields['address'] = forms.CharField(label='Shipping Address')
        self.fields['city'] = forms.CharField(label='Shipping City')
        self.fields['state'] = forms.CharField(label='Shipping State',min_length=2,max_length=5)
        self.fields['zip'] = forms.CharField(label='Shipping ZIP',min_length=5,max_length=5)
        self.fields['stripeToken'] = forms.CharField(widget=forms.HiddenInput)

    def clean_state(self):
        states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
        state = self.cleaned_data.get('state')
        if not state in states:
            raise forms.ValidationError('Please enter a valid state abbreviation')
        return state

    def clean_zip(self):
        zip = self.cleaned_data.get('zip')
        if len(zip) < 5 or len(zip) > 5:
            raise forms.ValidationError('Please enter a 5-digit zip code')
        try:
            int(zip)
        except:
            raise forms.ValidationError('Please enter numbers only')
        return zip

    def clean(self):
        token = self.cleaned_data.get('stripeToken')
        order = self.request.user.get_shopping_cart()
        #do NOT run the finalize method if the form has any errors
        if self.cleaned_data.get('state') is not None and self.cleaned_data.get('zip') is not None:
            try:
                order.finalize(token)
            except Exception as e:
                raise forms.ValidationError(e)
        return self.cleaned_data

    def commit(self):
        '''Process the form action'''
        #the form action was processed in the clean method - finalize()
        #update the order with shipping Information
        tracking = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        order = cmod.Order.objects.filter(user=self.request.user).order_by('-id')[0]
        order.ship_name = self.cleaned_data.get('name')
        order.ship_address = self.cleaned_data.get('address')
        order.ship_city = self.cleaned_data.get('city')
        order.ship_state = self.cleaned_data.get('state')
        order.ship_zip_code = self.cleaned_data.get('zip')
        order.ship_tracking = tracking
        order.ship_date = datetime.now() + timedelta(days=2)
        order.save()
