from django.test import TestCase
from account import models as amod
from django.contrib.auth.models import Permission, Group, ContentType

class UserModelTest(TestCase):

    fixtures = ['data.yaml']

    def setUp(self):
        self.u1 = amod.User.objects.get(email='marge@simpsons.com')

    def test_user_create_save_load(self):
        '''Test round trip of User model data to/from database'''

        u2 = amod.User.objects.get(email='marge@simpsons.com')
        self.assertEquals(self.u1.first_name, u2.first_name)
        self.assertEquals(self.u1.last_name, u2.last_name)
        self.assertEquals(self.u1.email, u2.email)
        self.assertEquals(self.u1.address, u2.address)
        self.assertEquals(self.u1.city, u2.city)
        self.assertEquals(self.u1.state, u2.state)
        self.assertEquals(self.u1.password, u2.password)

    def test_add_groups_check_permissions(self):
        '''Add groups to a users and check permissions'''

        g1 = Group.objects.get(id=101)
        self.u1.groups.add(g1)
        self.assertTrue(self.u1.has_perm('account.return_product'))

    def test_add_user_permissions_check_permissions(self):
        '''Add permissions to users and test some permissions'''

        p1 = Permission.objects.get(id=101)
        self.u1.user_permissions.add(p1)
        self.assertTrue(self.u1.has_perm('account.return_product'))


    def test_password(self):
        '''Test password with set_password() and check_password()'''

        u2 = amod.User()
        u2.set_password('password')
        self.assertTrue(u2.check_password('password'))

    def test_regular_field_changes(self):
        ''''''
        u2 = amod.User.objects.get(email='marge@simpsons.com')
        self.assertEquals(self.u1.first_name, u2.first_name)
        self.assertEquals(self.u1.last_name, u2.last_name)
        self.assertEquals(self.u1.email, u2.email)
        self.assertEquals(self.u1.address, u2.address)
        self.assertEquals(self.u1.city, u2.city)
        self.assertEquals(self.u1.state, u2.state)
        self.assertEquals(self.u1.password, u2.password)
