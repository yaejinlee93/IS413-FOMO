from django.db import models
from polymorphic.models import PolymorphicModel

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
