from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError

class HookrUser(User):
    """
	This is the hookr user class.
	It is bound to the django builtin User class.
	It contains an integerfield representing the number of points a user has
	"""
    points = models.IntegerField()
        
class Network(models.Model):
    """
	This is the network class.
	It represents the "networks" or "exchanges" that hookups and shares exist in.
	It has a name (which is a charfield) and a collection of HookrUsers.
	"""
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(HookrUser, related_name='u', blank=True, null=True)
    def add_user(self, user):
        self.users.add(user)
        self.save()
    def __unicode__(self):
        return self.name
    
class ClosedNetwork(models.Model):
    """
	This is the closed network class.
	It extends the functionality of a network to allow the creation of exclusive, "invitation only" networks
	It has a list of HookrUsers who have been invited (but have not accepted their invitations)
	"""
    invited_users = models.ManyToManyField(HookrUser, related_name='i', blank=True, null=True)
    def invite_user(self, user):
        self.invited_users.add(user)
        self.save()
    def add_user(self, user):
        try:
            self.invited_users.get(pk=user.id)
        except HookrUser.DoesNotExist:
            raise ValidationError("User tried to join private group uninvited")
            return
        self.invited_users.remove(user)
        self.users.add(user)
        self.save()
        
class HookrProfile(models.Model):
    """
	This is the hookr profile class.
    Hooker profiles belong to networks and represent people who hook up.
	Profiles have a firstname, lastname, network, and, optionally, a hookr user association.
	"""
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    user = models.ForeignKey(HookrUser, blank=True, null=True)
    network = models.ForeignKey(Network)
    def __unicode__(self):
        return self.firstname+' '+self.lastname

class Hookup(models.Model):
    """
	This is the hookup class.
    Hookups exist in the context of a particular network and are associated with Shares
	Hookups are associated with exactly two hookr profiles and one network
	"""
    DEFAULT_DIVIDEND = 1000
    hookers = models.ManyToManyField(HookrProfile)
    network = models.ForeignKey(Network)
    #TODO nickname polling system
    #nickname = models.CharField(max_length=255
    def save(self, *args, **kwargs):
        if((self.pk is None) or (self.hookers.count()==2)): #Need to allow initial save for manytomany relationship
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
    """
	This is the potential ipo class.
    Potential IPOs are hookups that are not yet associated with shares
	Potential IPOs have a number of requests for shares of their hookup
	and default information associated with IPOs (namely, volume and pricing)
	"""
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
    """
	This is the share group class.
    Share Groups are information about the purchases of a particular user
	Share Groups have a volume (the number of shares), a hookup, and an owner
	Two share groups should never have the same owner and hookup at the same time
	"""
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
    def save(self, is_first=False, *args, **kwargs):
        #Verify that this is the only sharegroup belonging to this user for this hookup, if not just add this volume to the other one
        #if(is_first):
        #    super(ShareGroup, self).save(*args, **kwargs)
        #    return
        try:
            other = ShareGroup.objects.get(hookup=self.hookup, owner=self.owner)
            if other!=self:
                other.volume+=self.volume
                other.save(is_first=True)
                return
        except ShareGroup.DoesNotExist:
            pass
        super(ShareGroup, self).save(*args, **kwargs)
                
class Order(models.Model):
    """
	This is the Order class.
    Orders are information about transactions involving share groups
	Orders are an abstract type extended by all actions that can be a performed by
	a user involving shares
	Orders have an associated hookup, price, and volume. They aditionally have
	DateTimeFields for when they were created and, optionally, when they expire
	"""
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
    """
	This is the sell order class.
    it contains validation necessary for selling shares
	"""
    def save(self, *args, **kwargs):
        shares = ShareGroup.objects.get(hookup=self.hookup, owner=self.owner)
        other_orders = SellOrder.objects.filter(hookup=self.hookup, owner=self.owner)
        reserved=0
        for order in other_orders:
            if order!=self:
                reserved+=order.volume
        if((shares.volume-reserved)<self.volume):
            raise ValidationError("User does not have enough shares for sell order")
        super(SellOrder, self).save(*args, **kwargs)
    
class BaseBuyOrder(Order):
    """
	This is the base class for buy orders.
    It is an abstract class. It contains validation necessary
    for buying shares and also ensures that a user's points
    are reserved unless the order is cancelled.
	"""
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
        super(BaseBuyOrder, self).save(*args, **kwargs)
    class Meta:
        abstract = True

class BuyOrder(BaseBuyOrder):
    """
    This is the buy order class.
    This is the non-abstract version of the BaseBuyOrder
    """
    pass

class IPOOrder(BaseBuyOrder):
    """
    This is the IPO order class.
    It is like a buy order except that the price is set as the default
    for IPOs.
    It should be associated with a PotentialIPO and not just a Hookup.
    """
    def save(self, *args, **kwargs):
        if type(self.hookup) == PotentialIPO:
            self.price = PotentialIPO.DEFAULT_PRICE
            super(IPOOrder, self).save(*args, **kwargs)
            ipo = PotentialIPO.objects.get(id=self.hookup.id)
            ipo.add_requests(self.volume)
            ipo.save()
        else:
            raise ValidationError("IPOOrder associated with Hookup (not PotentialIPO)")
