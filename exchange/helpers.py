from exchange.models import BuyOrder, SellOrder, HookrUser

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
