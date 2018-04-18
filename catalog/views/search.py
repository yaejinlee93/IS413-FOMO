from catalog import models as cmod
from django_mako_plus import view_function
from django.conf import settings
from django import forms
import requests
import json
import math
from django.http import JsonResponse
from django.contrib.auth.decorators import permission_required

@view_function
def process_request(request):
    results = []
    form = {}
    show = ''
    form['name'] = ''
    form['category'] = ''
    form['max_price'] = ''
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        max_price = request.POST.get('max_price')

        results = cmod.Product.objects.filter(status='A').exclude(name="TaxAmount")

        if len(name) > 0:
            results = results.filter(name__icontains=name)
            form['name'] = name
        if len(category) > 0:
            category = category.title()
            results = results.filter(category__name=category)
            form['category'] = category
        if len(max_price) > 0:
            results = results.filter(price__lte=max_price)
            form['max_price'] = max_price

        if not len(results) > 0:
            show = None

    context = {
        'results':results,
        'form':form,
        'show':show,
    }
    return request.dmp.render('search.html',context)

@permission_required('request.user.is_staff')
@view_function
def find(request):
    #example URL:
    #http://localhost:8000/catalog/search.find/?name=s&category=Instruments&max_price=500.00&page=1
    name = request.GET['name']
    category = request.GET['category']
    max_price = request.GET['max_price']
    page = request.GET['page']
    page = int(page)-1

    #filter the products
    all_products = cmod.Product.objects.filter(category__name=category, name__icontains=name, price__lte=max_price)
    page_count = all_products.count()
    start = page*6
    end = (page+1)*6
    if start > page_count:
        pass
    if end > page_count:
        end = page_count
    #show only 6 products per page
    show_products = all_products[start:end]

    #add the fields to the products
    products = []
    for p in show_products:
        products.append({'category__name':p.category.name, 'name':p.name,'price':p.price})

    search_result = {'Products':products}

    return JsonResponse(search_result, safe=False)
