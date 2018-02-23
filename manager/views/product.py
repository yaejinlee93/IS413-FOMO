from django_mako_plus import view_function
from django.http import HttpResponseRedirect
from catalog import models as cmod

@view_function
def process_request(request):

    product = cmod.Product.objects.filter(status='A')

    context = {
        'product' : product,
    }
    return request.dmp_render('product.html', context)
