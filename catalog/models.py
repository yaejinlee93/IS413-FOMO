from django.db import models
from polymorphic.models import PolymorphicModel
from django.conf import settings

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
            image_list = self.images.all()
        else:
            url = settings.STATIC_URL + "catalog/media/products/image_unavailable.gif/"
        return url

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
