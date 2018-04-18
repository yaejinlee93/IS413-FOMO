from django.conf import settings
from django_mako_plus import view_function, jscontext
from datetime import datetime, timezone
from catalog import models as cmod
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required
@view_function
def process_request(request, path=''):
    #utc_time = datetime.utcnow()
    cart = []
    past_cart = []
    order = request.user.get_shopping_cart()
    if order is not None:
        cart = order.active_items(False)
        past_order = order.all_items(False)
        for item in past_order:
            past_cart.append(item.product)
    else:
        if len(path) > 0:
            return HttpResponseRedirect(path)
        else:
            return HttpResponseRedirect('/catalog/index/')
    #tax_product = cmod.Product.objects.filter(name='TaxAmount').first()

    #recalculate the order to provide accuracy
    order.recalculate()
    tax_amount = order.tax_amount

    context = {
        # list of categories
        'cart' : cart,
        'past_cart' : past_cart,
        'tax_amount': tax_amount,
        'order': order,
    }
    return request.dmp.render('cart.html', context)

@view_function
def remove(request,item:cmod.OrderItem=None):
    if item is not None:
        item.status = 'deleted'
        item.quantity = 0
        item.save()
        order = item.order
        order.recalculate()
    return HttpResponseRedirect('/catalog/cart/')
