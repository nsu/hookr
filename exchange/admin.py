#!/usr/bin/env python
# TeamWon Design Group
# Programmer's Examples Notebook
# admin.py
# this file contains Django model
# Lou Fogel

from django.contrib import admin
from exchange.models import *

admin.site.register(HookrUser)
admin.site.register(Hookup)
admin.site.register(PotentialIPO)
admin.site.register(ShareGroup)
admin.site.register(SellOrder)
admin.site.register(IPOOrder)
admin.site.register(BuyOrder)
admin.site.register(Network)
admin.site.register(HookrProfile)
