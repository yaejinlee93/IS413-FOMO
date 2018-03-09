from django_mako_plus import view_function, jscontext
from django.http import HttpResponseRedirect
from catalog import models as cmod
import math

@view_function
def process_request(request, category:cmod.Category=None, pnum:int=1):

    categories = cmod.Category.objects.all()
    products = cmod.Product.objects.all()

    if category is not None:
        filtered_products = products.filter(category__id=category.id)
        num_page = math.ceil(filtered_products.count() / 6)
        cat_id = category.id
        cat_name = category.name

    else:
        num_page = math.ceil(products.count() / 6)
        filtered_products = products
        cat_id= 0
        cat_name = 'All Products'

    context = {
        jscontext('num_pages') : num_page,
        jscontext('cid') : cat_id,
        'category' : category,
        'categories' : categories,
        'num_pages' : num_page,
        'products' : products,
        'filtered_products' : filtered_products,
        'cat_name' : cat_name,

    }
    return request.dmp.render('index.html', context)

@view_function
def products(request, category:cmod.Category=None, pnum:int=1):
    products = cmod.Product.objects.all()

    if category is not None:
        filtered_products = products.filter(category__id=category.id)

    else:
        filtered_products = products

    six_items = filtered_products[(pnum - 1) * 6 : pnum * 6]


    context = {

        'filtered_products' : filtered_products,
        'six_items' : six_items,

    }

    return request.dmp.render('index.products.html',context)
