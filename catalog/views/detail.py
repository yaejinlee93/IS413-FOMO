from django_mako_plus import view_function, jscontext
from django.http import HttpResponseRedirect
from catalog import models as cmod
import math

def fix_html(x):
    x = x.replace("&","&amp")
    x = x.replace("<","&lt")
    x = x.replace(">","&gt")
    x = x.replace("\"","&quot")
    x = x.replace("\'","&#39")
    return x

@view_function
def process_request(request, product:cmod.Product=None):

    if product in request.last_five:
        request.last_five.remove(product)

    request.last_five.insert(0, product)

    if len(request.last_five) > 6:
        request.last_five.pop(-1)

    prod_name = fix_html(product.name)

    context = {
        'product' : product,
        'prod_name' : prod_name,
    }
    return request.dmp.render('detail.html', context)
