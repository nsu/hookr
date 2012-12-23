from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError

class HookrUser(User):
    points = models.IntegerField()
        
class Network(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(HookrUser, related_name='u', blank=True, null=True)
    def add_user(self, user):
        self.users.add(user)
        self.save()
    def __unicode__(self):
        return self.name
    
class ClosedNetwork(models.Model):
    invited_users = models.ManyToManyField(HookrUser, related_name='i', blank=True, null=True)
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
    def __unicode__(self):
        return self.firstname+' '+self.lastname

class Hookup(models.Model):
    DEFAULT_DIVIDEND = 1000
    hookers = models.ManyToManyField(HookrProfile)
    network = models.ForeignKey(Network)
    #TODO nickname polling system
    #nickname = models.CharField(max_length=255
    def save(self, *args, **kwargs):
        if((self.pk is None) or (self.hookers.count==2)): #Need to allow initial save for manytomany relationship
            super(Hookup, self).save(*args, **kwargs)
        else:
            raise ValidationError("There must be two hookers in a hookup")
        return
    
    def __unicode__(self):
        mystr=''
        for hooker in self.hookers.all():
            mystr=mystr+hooker.__unicode__()
        return mystr+'('+self.network.__unicode__()+')'
    
class PotentialIPO(Hookup):
    DEFAULT_VOLUME = 150
    DEFAULT_PRICE = 100
    num_requests = models.IntegerField(default=0)
    def convert_to_hookup(self):
        new_hookup = Hookup(network=self.network) #Make the new hookup (not just a potential IPO anymore)
        new_hookup.save()
        for hooker in self.hookers.all():
            new_hookup.hookers.add(hooker)
        new_hookup.save()
        for order in IPOOrder.objects.filter(hookup=self): #Distribute shares to users who first requested them
            if(self.num_requests!=0):
                if(order.volume>=self.num_requests):
                    new_share_group = ShareGroup(hookup=new_hookup, volume=self.num_requests, owner=order.owner) #distribute remaining shares
                    new_share_group.save()
                    self.num_requests=0
                else:
                    new_share_group = ShareGroup(hookup=new_hookup, volume=order.volume, owner=order.owner) #Give as many shares as were requested
                    new_share_group.save()
                    self.num_requests -= order.volume
            order.delete()
        self.delete()
        return new_hookup
    def add_requests(self, num_requests):
        self.num_requests += num_requests
        if self.num_requests>=PotentialIPO.DEFAULT_VOLUME: #Here goes the IPO
            self.num_requests = PotentialIPO.DEFAULT_VOLUME #We don't want to distribute more than this
            self.convert_to_hookup()
            self.delete()
            return
        self.save()
        return
        
class ShareGroup(models.Model):
    volume = models.IntegerField()
    hookup = models.ForeignKey(Hookup)
    owner = models.ForeignKey(HookrUser)
    def selloff(self, volume):
        if volume>self.volume:
            raise ValidationError("Tried to sell more shares than existed")
        self.volume -= volume
        if self.volume == 0:
            self.delete()
        else:
            self.save()
    def add_shares(self, volume):
        self.volume += volume
        self.save()   
                
class Order(models.Model):
    hookup = models.ForeignKey(Hookup)
    owner = models.ForeignKey(HookrUser)
    price = models.IntegerField()
    volume = models.IntegerField()
    create_time = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(blank=True, null=True)
    def cancel(self):
        self.delete()
    class Meta:
        abstract = True
        get_latest_by = 'create_time'
        ordering = ['create_time']
    def __unicode__(self):
        return self.hookup.__unicode__()+'('+self.owner.__unicode__()+')'
        
class SellOrder(Order):
    def save(self, *args, **kwargs):
        shares = ShareGroup.objects.get(hookup=self.hookup, owner=self.owner)
        if(shares.volume<self.volume):
            raise ValidationError("User does not have enough shares for sell order")
        super(SellOrder, self).save(*args, **kwargs)
    
class BuyOrder(Order):
    def reserve_funds(self):
        self.owner.points -= self.price*self.volume
        self.owner.save()
    def cancel(self):
        self.owner.points += self.price*self.volume
        self.owner.save()
        self.delete()
    def save(self, *args, **kwargs):
        if(self.owner.points<(self.price*self.volume)):
            raise ValidationError("User does not have enough points for buy order")
        super(BuyOrder, self).save(*args, **kwargs)

class IPOOrder(BuyOrder):
    def save(self, *args, **kwargs):
        self.price = PotentialIPO.DEFAULT_PRICE
        super(BuyOrder, self).save()
        self.hookup.add_requests(self.volume)
        self.hookup.save(*args, **kwargs)
