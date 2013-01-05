from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.http import HttpResponse
from django.core import serializers
from exchange.models import *
from exchange.views import match_orders
from exchange.serializers import *
@dajaxice_register
def sayhello(request):
    return simplejson.dumps({'message':'Hello World'})
    
@dajaxice_register(method='GET')
def get_my_hookups(request):
    my_shares = ShareGroup.objects.filter(owner=request.user)
    hookups = [share.hookup for share in my_shares]
    ser=JSONSerializer()
    data = ser.serialize(hookups, relations='hookers, network')
    return data
    
@dajaxice_register
def place_sell_order(request, volume, price, hookup_pk):
    hookup = Hookup.objects.get(pk=hookup_pk)
    #TODO figure out what response objects to use
    try:
        ShareGroup.objects.get(owner=request.user)
        order = SellOrder(owner=request.user, volume=volume, price=price)
        order.save()
        buyers = BuyOrder.objects.get(hookup=hookup)
        for buy_order in buyers:
            match_orders(buy_order, order)
            #if the order is empty it will delete itself
            if order is None:
                break
    except ShareGroup.DoesNotExist, SellOrder.ValidationError:
        #User doesn't seem to own enough of these...
        return False

@dajaxice_register
def place_buy_order(request, volume, price, hookup_pk):
    hookup = Hookup.objects.get(pk=hookup_pk)
    user = HookrUser.objects.get(id=request.user.id)
    #TODO figure out what response objects to use
    try:
        order = BuyOrder(owner=request.user, volume=volume, price=price)
        order.save()
        sellers = BuyOrder.objects.get(hookup=hookup)
        for sell_order in sellers:
            match_orders(order, sell_order)
            #if the order is empty it will delete itself
            if order is None:
                break
    except BuyOrder.ValidationError:
        #User doesn't seem to own have enough points...
        return False
