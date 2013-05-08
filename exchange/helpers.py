from exchange.models import BuyOrder, SellOrder, HookrUser, ShareGroup, PriceDatapoint
import datetime
from django.utils.timezone import utc

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
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        datapoint = PriceDatapoint(hookup=hookup, price=price, volume=volume, time=now)
        #save all of the objects we just modified (holy shit!)
        datapoint.save()
        buy_order.save()
        sell_order.save()
        old_group.save()
        new_group.save()
        buyer.save()
        seller.save()
        
def pay_dividends(hookup):
    #find the market value of the hookup (mean price of last 10% of sales)
    shares = ShareGroup.objects.filter(hookup=hookup)
    datapoints = PriceDatapoint.objects.filter(hookup=hookup)
    volume=0
    for datapoint in datapoints:
        volume += datapoint.volume
    #we only want the most recent sales (last 10%)
    volume /= 10
    counted = 0
    price = 0
    for datapoint in datapoints:
        if datapoint.volume+counted < volume:
            price += datapoint.price*datapoint.volume
            counted += datapoint.volume
        else:
            price += (volume-counted) * datapoint.price
            counted = volume
            break
    meanprice = price/volume
    #pay out 110% of market value as dividend and delete all shares
    for group in shares:
        user = group.owner
        user.points += float(meanprice) * group.volume * 1.1
        group.delete()
        user.save()
    #it's over now, delete the hookup
    hookup.delete()
