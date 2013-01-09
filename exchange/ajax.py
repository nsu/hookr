from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.http import HttpResponse
from django.core import serializers
from exchange.models import *
from exchange.helpers import match_orders
from django.db.models import Q
from exchange.serializers import *

@dajaxice_register
def sayhello(request):
    return simplejson.dumps({'message':'Hello World'})

@dajaxice_register(method='GET')
def get_my_hookups(request):
    my_shares = ShareGroup.objects.filter(owner=request.user)
    hookups = [share.hookup for share in my_shares]
    serializer=JSONSerializer()
    data = serializer.serialize(hookups, relations='hookers, network')
    return data

@dajaxice_register
def place_sell_order(request, volume, price, hookup_pk):
    hookup = Hookup.objects.get(pk=hookup_pk)
    try:
        ShareGroup.objects.get(owner=request.user)
        order = SellOrder(owner=request.user, volume=volume, price=price)
        order.save()
        serializer=JSONSerializer()
        buyers = BuyOrder.objects.get(hookup=hookup)
        for buy_order in buyers:
            match_orders(buy_order, order)
            #if the order is empty it will delete itself and return nothing
            if order is None:
                return None
        order = SellOrder.objects.get(id=order.id)
        #return the order to the user
        return serializer.serialize(order)
    except ShareGroup.DoesNotExist, SellOrder.ValidationError:
        #User doesn't seem to own enough of these...
        error = AjaxError("You cannot sell shares that you do not own.")
        return error.to_json()

@dajaxice_register
def place_buy_order(request, volume, price, hookup_pk):
    hookup = Hookup.objects.get(pk=hookup_pk)
    try:
        order = BuyOrder(owner=request.user, volume=volume, price=price)
        order.save()
        sellers = BuyOrder.objects.get(hookup=hookup)
        for sell_order in sellers:
            match_orders(order, sell_order)
            #if the order is empty it will delete itself and return nothing
            if order is None:
                return None
        order = BuyOrder.objects.get(id=order.id)
        #return the order to the user
        return serializer.serialize(order)
    except BuyOrder.ValidationError:
        #User doesn't seem to own have enough points...
        error = AjaxError("You do not have enough points to place this order.")
        return error.to_json()

@dajaxice_register
def get_price_inquiry(request, volume, hookup_pk):
    hookup = Hookup.objects.get(pk=hookup.pk)
    orders = SellOrder.objects.order_by('price')
    cost = 0
    for order in orders:
        if order.volume > volume:
            volume = 0
            cost += volume*order.price
        else:
            volume -= order.volume
            cost += order.volume*order.price
        if volume == 0:
            return cost
    error = AjaxError("Not enough shares are for sale")
    return error.to_json()
    
@dajaxice_register
def profile_search(request, name=None):
    networks = request.user.u.all()
    names = HookrProfile.objects.filter(Q(firstname__icontains=name)|Q(lastname__icontains=name),Q(network__in=networks))
    serializer = JSONSerializer()
    data = serializer.serialize(names, relations='network')
    return data

@dajaxice_register
def get_hookup_from_profiles(request, profile1pk, profile2pk):
    profile_pks = {profile1pk, profile2pk}
    profiles = HookrProfile.objects.filter(pk__in=profiles)
    try:
        hookup = Hookup.objects.get(profile__in=profiles)
        serializer=JSONSerializer()
        data = serializer.serialize(hookup, relations='hookers, network')
    except Hookup.DoesNotExist:
        error = AjaxError("A hookup with specified profiles does not exist.")
        data = error.to_json()
    return data

class AjaxError(object):
    def __init__(self, message):
        self.message=message
    
    def to_json(self):
        return "{'type':'error','message':'%s'}" % (self.message)
