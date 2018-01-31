from django.db import models
from cuser.models import AbstractCUser

class User(AbstractCUser):
    birthdate = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)

    def get_purchases(self):
        return [ 'Roku Ultimate 2000', 'USB Cable', 'Computer' ]
