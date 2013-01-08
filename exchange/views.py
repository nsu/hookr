from django.http import HttpResponse, HttpResponseRedirect
from django.forms import ModelForm
from exchange.forms import HookupForm, IPOOrderForm, BuyOrderForm
from exchange.models import *
from django.db.models import Q
from django.template import Context, loader
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def join_network(request, network):
    network.add_user(request.user)
    return HTTPResponse("Added User")

@login_required
def order_ipo(request, network):
    network=Network.objects.get(name=network)
    if request.method == 'POST':
        form = IPOOrderForm(network, request.POST)
        if form.is_valid():
            hookr_user=HookrUser.objects.get(id=request.user.id)
            hookup=form.cleaned_data['hookup']
            volume=form.cleaned_data['volume']
            new_order=IPOOrder(hookup=hookup, volume=volume, owner=hookr_user)
            new_order.save()
            new_order.reserve_funds()
            return HttpResponse('True')
        else:
            return HttpResponse('False')
    else:
        form = IPOOrderForm(network)
        return render(request, 'formTemplate.html',{
            'form': form
        })
        
@login_required
def order(request, network):
    network=Network.objects.get(name=network)
    if request.method == 'POST':
        form = BuyOrderForm(network, request.POST)
        if form.is_valid():
            hookr_user=HookrUser.objects.get(id=request.user.id)
            hookup=form.cleaned_data['hookup']
            volume=form.cleaned_data['volume']
            new_order=BuyOrder(hookup=hookup, volume=volume, owner=hookr_user)
            new_order.save()
            new_order.reserve_funds()
            return HttpResponse('True')
        else:
            return HttpResponse('False')
    else:
        form = BuyOrderForm(network)
        return render(request, 'formTemplate.html', {
            'form': form
        })

@login_required
def make_hookup(request, network):
    network = Network.objects.get(name=network)
    if request.method == 'POST':
        form = HookupForm(network, request.POST)
        if form.is_valid():
            hookers = form.cleaned_data['hookers']
            try:
                hookup = PotentialIPO.objects.get(network=network, hookers=hookers)
            except:
                hookup = PotentialIPO(network=network, num_requests=0)
                hookup.save()
                hookup.hookers.add(hookers[0])
                hookup.hookers.add(hookers[1])
                print hookup.hookers.count
                hookup.save()
            return HttpResponse('True')
        else:
            return HttpResponse('False')
    else:
        form = HookupForm(network)
        return render(request, 'formTemplate.html',{
            'form': form
        })

def match_orders(buy_order, sell_order):
    hookup = sell_order.hookup
    if buy_order.hookup != hookup:
        return
    if buy_order.price>sell_order.price:
        price = sell_order.price
        if buy_order.volume>sell_order.volume:
            volume = sell_order.volume
        else:
            volume = buy_order.volume
        buy_order.volume -= volume
        sell_order.volume -= volume
        seller = sell_order.owner
        buyer = buy_order.owner
        seller.points += price*volume
        buyer.points -= price*volume
        old_group = ShareGroup.objects.get(owner=seller, hookup=hookup)
        new_group = ShareGroup(owner=buyer, hookup=hookup, volume=volume)
        old_group.volume -= volume
        buy_order.save()
        sell_order.save()
        old_group.save()
        new_group.save()
        buyer.save()
        seller.save()
        
@login_required
def homepage(request):
    return render(request, 'home.html', makeContext(user))
