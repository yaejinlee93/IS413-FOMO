from django.db import models
from cuser.models import AbstractCUser
from catalog import models as cmod
from datetime import datetime

class User(AbstractCUser):
    address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)

    #Get or create order object. status == cart
    def get_shopping_cart(self):

        o1 = cmod.Order.objects.filter(user=self, name='Shopping Cart').first()
        if o1 is None:
            #create a new order
            o1 = cmod.Order()
            o1.user = self
            o1.order_date = datetime.now()
            o1.name = 'Shopping Cart'
            o1.status = 'cart'
            o1.save()

            #add the tax product
            # tax_product = cmod.Product.objects.filter(name='TaxAmount').first()
            # p1 = o1.get_item(tax_product,True)
            # p1.description = 'TaxAmount'
            # p1.save()
        return o1
