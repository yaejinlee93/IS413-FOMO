from django.test import TestCase
from account import models as amod

class UserModelTest(TestCase):

    def setUp(self):
        self.u1 = amod.User()
        self.u1.first_name = 'Marge'
        self.u1.last_name = 'Simpson'
        self.u1.email = 'marge@simpsons.com'
        self.u1.set_password('password')
        # ... more fields
        self.u1.save()

    def test_user_create_save_load(self):
        '''Test round trip of User model data to/from database'''

        u2 = amod.User.objects.get(email=u1.email)
        self.assertEquals(u1.first_name, u2.first_name)
        self.assertEquals(u1.last_name, u2.last_name)
        self.assertEquals(u1.email, u2.email)
        self.assertEquals(u1.password, u2.password)
        self.assertTrue(u2.check_password('password'))

    def test_add_groups_check_permissions(self):
        '''Add groups to a user and check permissions'''
        a = 1
        self.assertEqual(a, 1)
