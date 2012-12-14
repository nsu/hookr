from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError

class HookrUser(User):
    points = models.IntegerField()
    
class Hookup(models.model):
    hookers = Models.ManyToManyField(HookrUser)
    def create(self, hooker1, hooker2)
        self.hookers.clear() #This should ensure that there are only two hookers
        self.save() #Need a Primary Key before we can add hookers
        self.hookers.add(hooker1)
        self.hookers.add(hooker2)
        self.save()
    def clean(self):
        if(len(self.hookers.all())!=2):
            raise ValidationError("Number of hookers not equal to 2!")

class Share(models.model):
    hookup = models.ForeignKey(Hookup)
    owner = models.ForeignKey(HookrUser)

class Order(models.model):
    hookup = models.ForeignKey(Hookup)
    owner = models.ForeignKey(HookrUser)
    price = models.IntegerField()
    volume = models.IntegerField()
    createtime = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()
    def clean(self):
        if (self.createtime<self.expiration):
            raise ValidationError("Order expired before it was created")
    class Meta:
        abstract = True
        
class SellOrder(Order):
    def clean(self):
        super.clean()
        shares = Shares.objects.filter(hookup=self.hookup, owner=self.owner)
        if(len(shares)<self.volume):
            raise ValidationError("User does not have enough points for buy order")
    
class BuyOrder(Order):
    def clean(self):
        super.clean()
        if(self.owner.points<(self.price*self.volume)):
            raise ValidationError("User does not have enough points for buy order")

