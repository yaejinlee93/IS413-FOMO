from django_mako_plus import view_function
from django.http import HttpResponseRedirect
from catalog import models as cmod

@view_function
def process_request(request, product:cmod.Product):

    #p = cmod.Product.objects.get(id=request.urlparams[0])

    product.status = 'I'
    product.save()

    return HttpResponseRedirect('/manager/product')

    context = {

    }
    return request.dmp.render('delete.html', context)
