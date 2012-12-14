from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ValidationError


def validate_two(value):
    if len(value) != 2:
        raise ValidationError(u'field should have two values, has {} instead'.format(len(value))


class HookrUser(User):
    points = models.IntegerField()
    
class Hookup(models.Model):
    hookers = models.ManyToManyField(HookrUser, validators=[validate_two])

class Share(models.Model):
    hookup = models.ForeignKey(Hookup)
    owner = models.ForeignKey(HookrUser)

class Order(models.Model):
    hookup = models.ForeignKey(Hookup)
    owner = models.ForeignKey(HookrUser)
    price = models.IntegerField()
    volume = models.IntegerField()
    createtime = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()
    class Meta:
        abstract = True
        
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

