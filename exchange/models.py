from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError

class HookrUser(User):
    points = models.IntegerField()
        
    
class Network(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(HookrUser, related_name='u')
    def add_user(self, user):
        self.users.add(user)
        self.save()
        
class ClosedNetwork(models.Model):
    invited_users = models.ManyToManyField(HookrUser, related_name='i')
    def invite_user(self, user):
        self.invited_users.add(user)
        self.save()
    def add_user(self, user):
        try:
            self.invited_users.get(pk=user.id)
        except:
            raise ValidationError("User tried to join private group uninvited")
            return
        self.invited_users.remove(user)
        self.users.add(user)
        self.save()
        
class HookrProfile(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    user = models.ForeignKey(HookrUser, blank=True, null=True)
    network = models.ForeignKey(Network)

class Hookup(models.Model):
    #TODO figure out how to enforce only two hookers
    hookers = models.ManyToManyField(HookrProfile)
    network = models.ForeignKey(Network) 

class Share(models.Model):
    hookup = models.ForeignKey(Hookup)
    owner = models.ForeignKey(HookrUser)
        
class PotentialIPO(Hookup):
    DEFAULT_VOLUME = 100;
    DEFAULT_PRICE = 100;
    num_requests = models.IntegerField()
    def add_requests(self, num_requests):
        self.num_requests += num_requests
        if self.num_requests>PotentialIPO.DEFAULT_VOLUME:
            #TODO convert to hookup and distribute shares
            pass
        self.save()   
                
class Order(models.Model):
    hookup = models.ForeignKey(Hookup)
    owner = models.ForeignKey(HookrUser)
    price = models.IntegerField()
    volume = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(blank=True, null=True)
    class Meta:
        abstract = True
        get_latest_by = 'create_time'
        ordering = ['create_time']
        
class SellOrder(Order):
    def save(self):
        shares = Shares.objects.filter(hookup=self.hookup, owner=self.owner)
        if(len(shares)<self.volume):
            raise ValidationError("User does not have enough points for buy order")
        super(SellOrder, self).save()
    
class BuyOrder(Order):
    def save(self):
        if(self.owner.points<(self.price*self.volume)):
            raise ValidationError("User does not have enough points for buy order")
        super(BuyOrder, self).save()

class IPOOrder(Order):
    def save(self):
        self.price = PotentialIPO.DEFAULT_PRICE
        self.hookup.add_requests(self.volume)
