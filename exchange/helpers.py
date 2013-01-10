from exchange.models import BuyOrder, SellOrder, HookrUser, ShareGroup, PriceDatapoint
from datetime import datetime

def match_orders(buy_order, sell_order):
    #get the hookup for the sell order
    hookup = sell_order.hookup
    #are we talking about the same hookup? if not, then there won't be a sale
    if buy_order.hookup != hookup:
        return
    #if the buyer is willing to pay the seller's price
    if buy_order.price>=sell_order.price:
        price = sell_order.price
        #determine limiting factor for volume
        if buy_order.volume>sell_order.volume:
            volume = sell_order.volume
        else:
            volume = buy_order.volume
        #decement volumes (remember that the save() function of an order will delete those with 0 volume)
        buy_order.volume -= volume
        sell_order.volume -= volume
        #get the users
        seller = sell_order.owner
        buyer = buy_order.owner
        #money changes hands
        seller.points += price*volume
        buyer.points -= price*volume
        #shares change hands (remember that the save() function of a share group will make sure there is only one group per user per hookup)
        old_group = ShareGroup.objects.get(owner=seller, hookup=hookup)
        new_group = ShareGroup(owner=buyer, hookup=hookup, volume=volume)
        old_group.volume -= volume
        #log this sale for price data
        datapoint = PriceDatapoint(hookup=hookup, price=price, volume=volume, time=datetime.now())
        #save all of the objects we just modified (holy shit!)
        datapoint.save()
        buy_order.save()
        sell_order.save()
        old_group.save()
        new_group.save()
        buyer.save()
        seller.save()
