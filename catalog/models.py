from django.db import models, transaction
from django.conf import settings
from django.forms.models import model_to_dict
from polymorphic.models import PolymorphicModel
from decimal import Decimal
from datetime import datetime
import stripe
from catalog import models as cmod

#######################################################################
###   Products

# Create Product and Category models

class Category(models.Model):
    name = models.TextField()
    description = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(PolymorphicModel):

    #forms. dropdown
    TYPE_CHOICES = (
        ('BulkProduct', 'Bulk Product'),
        ('IndividualProduct', 'Individual Product'),
        ('RentalProduct','Rental Product'),
    )
    STATUS_CHOICES = (
        ('A','Active'),
        ('I','Inactive'),
    )

    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    create_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    status = models.TextField(choices=STATUS_CHOICES, default='A')

    def image_url(self):
        '''Always returns an image'''
        if self.images.exists():
            url = settings.STATIC_URL + "catalog/media/products/" + self.images.first().filename
        else:
            url = settings.STATIC_URL + "catalog/media/products/image_unavailable.gif/"
        return url
        #if not return unavailable image

    def image_urls(self):
        '''Returns a list of images
        If no image, return unavailable
        will not return an empty list'''
        if self.images.exists():
            image_list = []
            for img in self.images.all():
                image_list.append(settings.STATIC_URL + "catalog/media/products/" + img.filename)
        else:
            image_list = [settings.STATIC_URL + "catalog/media/products/image_unavailable.gif/"]
        return image_list

class BulkProduct(Product):
    TITLE = 'Bulk'
    quantity = models.IntegerField()
    reorder_trigger = models.IntegerField()
    reorder_quantity = models.IntegerField()

    def get_quantity(self):
        return self.quantity

class IndividualProduct(Product):
    TITLE = 'Individual'
    itemID = models.TextField()

    def get_quantity(self):
        return 1

class RentalProduct(Product):
    TITLE = 'Rental'
    itemID = models.TextField()
    max_rental_days = models.IntegerField(default=0)
    retire_date = models.DateField(null=True, blank=True)

    def get_quantity(self):
        return 1

#ProductImage model

class ProductImage(models.Model):
    filename = models.TextField()
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)

#######################################################################
###   Orders

class Order(models.Model):
    '''An order in the system'''
    STATUS_CHOICES = (
        ( 'cart', 'Shopping Cart' ),
        ( 'payment', 'Payment Processing' ),
        ( 'sold', 'Finalized Sale' ),
    )
    order_date = models.DateTimeField(null=True, blank=True)
    name = models.TextField(blank=True, default="Shopping Cart")
    status = models.TextField(choices=STATUS_CHOICES, default='cart', db_index=True)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2, default=0) # max number is 999,999.99
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0) # max number is 999,999.99
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0) # max number is 999,999.99
    user = models.ForeignKey('account.User', related_name='orders',  on_delete=models.CASCADE)
    # shipping information
    ship_date = models.DateTimeField(null=True, blank=True)
    ship_tracking = models.TextField(null=True, blank=True)
    ship_name = models.TextField(null=True, blank=True)
    ship_address = models.TextField(null=True, blank=True)
    ship_city = models.TextField(null=True, blank=True)
    ship_state = models.TextField(null=True, blank=True)
    ship_zip_code = models.TextField(null=True, blank=True)

    def __str__(self):
        '''Prints for debugging purposes'''
        return 'Order {}: {}: {}'.format(self.id, self.user.get_full_name(), self.total_price)

    def all_items(self, include_tax_item=False):
        '''Returns all items for this order'''
        items = OrderItem.objects.filter(order=self).exclude(description='TaxAmount')
        if include_tax_item:
            items = OrderItem.objects.filter(order=self)
        return items

    def active_items(self, include_tax_item=True):
        '''Returns the active items on this order'''
        # create a query object (filter to status='active')
        items = OrderItem.objects.filter(order=self, status='active').exclude(description='TaxAmount')
        # if we aren't including the tax item, alter the
        # query to exclude that OrderItem
        if include_tax_item:
            items = OrderItem.objects.filter(order=self, status='active')
            #items.delete('TaxAmount')
        # I simply used the product name (not a great choice,
        # but it is acceptable for credit)
        return items


    def get_item(self, product, create=False):
        '''Returns the OrderItem object for the given product'''
        item = OrderItem.objects.filter(order=self, product=product).first()
        if item is None and create:
            item = OrderItem.objects.create(order=self, product=product, price=product.price, quantity=0)

        elif create and item.status != 'active':
            item.status = 'active'
            item.quantity = 0
        if item is not None:
            item.recalculate()
            item.save()
        return item


    def num_items(self):
        '''Returns the number of items in the cart'''
        return sum(self.active_items(include_tax_item=False).values_list('quantity', flat=True))


    def recalculate(self):
        '''
        Recalculates the total price of the order,
        including recalculating the taxable amount.

        Saves this Order and all child OrderLine objects.
        '''
        # iterate the order items (not including tax item) and get the total price
        # call recalculate on each item
        current_price = 0.0
        for item in self.active_items(False):
            current_price += float(item.price) * float(item.quantity)
            item.recalculate()
        # update/create the tax order item (calculate at 7% rate)
        tax_item = cmod.OrderItem.objects.filter(order=self,description='TaxAmount').first()
        self.tax_amount = current_price * 0.07
        # update the total and save
        self.subtotal = current_price
        self.total_price = current_price + self.tax_amount
        self.save()

    def finalize(self, stripe_charge_token):
        '''Runs the payment and finalizes the sale'''
        try:
            with transaction.atomic():
                # recalculate just to be sure everything is updated
                self.recalculate()
                # check that all products are available
                for item in self.active_items(False):
                    current_product = item.product
                    if current_product.status != 'A':
                        raise Exception(str(current_product) + ' is not available')
                    if hasattr(current_product,'quantity'):
                        if item.quantity > current_product.quantity:
                            raise Exception('Not enough quantity available')

                # contact stripe and run the payment (using the stripe_charge_token)
                #charge the card
                charge = stripe.Charge.create(
                  amount=int(self.total_price * 100),
                  currency="usd",
                  description="Example charge",
                  source=stripe_charge_token,
                )
                # finalize (or create) one or more payment objects
                pmt = Payment()
                pmt.order = self
                pmt.payment_date = datetime.now()
                pmt.amount = self.total_price
                pmt.validation_code = stripe_charge_token
                pmt.save()

                # set order status to sold and save the order
                o1 = self
                o1.status = 'sold'
                o1.name = 'Finalized Sale'
                o1.save()

                # update product quantities for BulkProducts
                for item in self.active_items(False):
                    current_product = item.product
                    if hasattr(current_product, 'quantity'):
                        current_product.quantity -= item.quantity
                        current_product.save()
                # update status for IndividualProducts
                for item in self.active_items(False):
                    current_product = item.product
                    if not hasattr(current_product,'quantity'):
                        current_product.status = 'I'
                        current_product.save()
        except Exception as e:
            return e

class OrderItem(PolymorphicModel):
    '''A line item on an order'''
    STATUS_CHOICES = (
        ( 'active', 'Active' ),
        ( 'deleted', 'Deleted' ),
        ( 'sold', 'Sold' ),
    )
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    status = models.TextField(choices=STATUS_CHOICES, default='active', db_index=True)
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0) # max number is 999,999.99
    quantity = models.IntegerField(default=0)
    extended = models.DecimalField(max_digits=8, decimal_places=2, default=0) # max number is 999,999.99

    def __str__(self):
        '''Prints for debugging purposes'''
        return 'OrderItem {}: {}: {}'.format(self.id, self.product.name, self.extended)


    def recalculate(self):
        '''Updates the order item's price, quantity, extended'''
        # update the price if it isn't already set and we have a product
        if self.product is not None:
            self.price = self.product.price
        # default the quantity to 1 if we don't have a quantity set
            #if self.quantity == 0:
                #self.quantity = 1
        # calculate the extended (price * quantity)
            self.extended = self.price * self.quantity
        # save the changes
        self.save()


class Payment(models.Model):
    '''A payment on a sale'''
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2) # max number is 999,999.99
    validation_code = models.TextField(null=True, blank=True)
