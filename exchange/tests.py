"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from exchange.models import *
from django.core.exceptions import ValidationError
from exchange import helpers
import datetime
from django.utils.timezone import utc

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
        # has 1805 points, cost is 1806
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
    def test_order_matching(self):
        sell_order = SellOrder(hookup = self.hookup, volume = 10, price = 100, owner = self.user)
        buy_order = BuyOrder(hookup = self.hookup, volume = 1, price = 100, owner = self.user)
        sell_order.save()
        buy_order.save()
        helpers.match_orders(buy_order, sell_order)
        self.assertEqual(sell_order.volume, 9)

class DividendTest(TestCase):
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
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        datapoint = PriceDatapoint(volume=1000, price=2000, hookup=self.hookup, time=now)
        datapoint.save()
        sharegroup = ShareGroup(owner = self.user, hookup = self.hookup, volume = 100)
        sharegroup.save()

    def test_make_report(self):
        report = Report(hookup=self.hookup, owner=self.user)
        report.save()
        self.assertIsNotNone(report.pk)
        
    def test_report_validation(self):
        report = Report(hookup=self.hookup, owner=self.user)
        report.save()
        report2 = Report(hookup=self.hookup, owner=self.user)
        report2.save()
        self.assertIsNone(report2.pk)
        
    def test_payout(self):
        prevpoints = self.user.points
        helpers.pay_dividends(self.hookup)
        self.user=HookrUser.objects.get(pk=self.user.pk)
        newpoints = self.user.points
        self.assertEqual(newpoints-prevpoints, 220000)
            
