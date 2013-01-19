"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from exchange.models import *
from django.core.exceptions import ValidationError

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
        
class SalesTest(TestCase):
    fixtures = ['one_test_hookup.json']
    
    def setUp(self):
        self.network = Network(name='Test Network')
        self.network.save()
        self.testprofile = HookrProfile(firstname='Test', lastname='User', network=self.network)
        self.test2profile = HookrProfile(firstname='Geoffery', lastname='Winnebago', network=self.network)
        self.testprofile.save()
        self.test2profile.save()
        self.hookup = Hookup(network=self.network)
        self.hookup.save()
        self.hookup.hookers.add(self.testprofile)
        self.hookup.hookers.add(self.test2profile)
        self.hookup.save()
        self.user = HookrUser.objects.get()
        sharegroup = ShareGroup(owner = self.user, hookup = self.hookup, volume = 10)
        sharegroup.save()
        
    def test_make_sell_order(self):
        order = SellOrder(hookup = self.hookup, volume = 10, price = 100, owner = self.user)
        order.save()
        self.assertTrue(order.pk is not None) #make sure it saved
        
    def test_make_buy_order(self):
        order = BuyOrder(hookup = self.hookup, volume = 1, price = 1805, owner = self.user)
        order.save()
        self.assertTrue(order.pk is not None) #make sure it saved
    
    def test_buy_order_validation(self):
        #User has 1805 points, cost is 1806
        order = BuyOrder(hookup = self.hookup, volume = 1, price = 1806, owner = self.user)
        try:
            order.save()
        except ValidationError:
            pass
        self.assertTrue(order.pk is None) #make sure didn't save
    
    def test_sell_order_validation(self):
        #user only has 10 shares
        order = SellOrder(hookup = self.hookup, volume = 11, price = 100, owner = self.user)
        try:
            order.save()
        except ValidationError:
            pass
        self.assertTrue(order.pk is None) #make sure didn't save
    #TODO def test_order_matching(self):
