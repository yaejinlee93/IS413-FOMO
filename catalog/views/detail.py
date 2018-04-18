from django_mako_plus import view_function, jscontext
from django.http import HttpResponseRedirect
import math
from django import forms
from formlib import Formless
from account import models as amod
from catalog import models as cmod

def fix_html(x):
    x = x.replace("&","&amp")
    x = x.replace("<","&lt")
    x = x.replace(">","&gt")
    x = x.replace("\"","&quot")
    x = x.replace("\'","&#39")
    return x

def set_prod(x):
    global my
    my = x

def get_prod():
    return my

@view_function
def process_request(request, product:cmod.Product=None):

    #
    if product is None:
        return HttpResponseRedirect('/catalog/index/')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/account/login/?next=/catalog/detail/'+str(product.id)+'/')
    set_prod(product)
    form = MyForm(request)
    if form.is_valid():
        form.commit()
        return HttpResponseRedirect('/catalog/cart/')

    Formless.submit_text = 'Add to Cart'

    #
    if product in request.last_five:
        request.last_five.remove(product)

    request.last_five.insert(0, product)

    if len(request.last_five) > 6:
        request.last_five.pop(-1)

    prod_name = fix_html(product.name)

    context = {
        'product' : product,
        'prod_name' : prod_name,
        'form' : form,
    }
    return request.dmp.render('detail.html', context)

class MyForm(Formless):
    '''Cart Form'''
    def init(self):
        '''Adds the fields for this form'''
        self.fields['product'] = forms.IntegerField(initial=get_prod().id,widget=forms.HiddenInput)
        if hasattr(get_prod(),'quantity'):
            self.fields['quantity'] = forms.IntegerField(label='Quantity',initial=1,widget=forms.NumberInput(attrs={'class': 'mynum'}))
        else:
            self.fields['quantity'] = forms.IntegerField(label='Quantity',initial=1,widget=forms.HiddenInput)

    def clean_product(self):
        current_product = cmod.Product.objects.filter(id = self.cleaned_data.get('product')).first()
        if current_product is None:
            raise forms.ValidationError('Product is sold out')
        return current_product

    def clean(self):
        #check the QUANTITY
        current_quantity = self.cleaned_data.get('quantity')
        current_product = get_prod()
        current_order = self.request.user.get_shopping_cart()
        order_item = cmod.OrderItem.objects.filter(order=current_order, product=current_product).first()
        if order_item is None:
            if current_quantity > current_product.get_quantity():
                num_cart = 0
                if order_item is not None:
                    num_cart = order_item.quantity
                raise forms.ValidationError('You have ' + str(num_cart) + ' in your cart. Number available is ' + str(current_product.get_quantity()) + '.')
        elif current_quantity + order_item.quantity > current_product.get_quantity():
            raise forms.ValidationError('You have ' + str(order_item.quantity) + ' in your cart. Number available is ' + str(current_product.get_quantity()) + '.')

        if current_quantity < 1:
            raise forms.ValidationError('Please select at least one')
        return self.cleaned_data

    def commit(self):
        '''Process the form action'''
        prod = get_prod()
        #update the database
        #get/create an order
        o1 = self.request.user.get_shopping_cart()

        item = o1.get_item(prod,False)
        if item is None:
            item = o1.get_item(prod,True)
            item.description = prod.description
        elif item.status != 'active':
            item = o1.get_item(prod,True)
        item.quantity += self.cleaned_data.get('quantity')
        item.price = prod.price
        item.save()
        item.recalculate()
        o1.recalculate()
