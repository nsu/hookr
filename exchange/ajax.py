from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from django.core import serializers
from exchange import models

@dajaxice_register
def sayhello(request):
    return simplejson.dumps({'message':'Hello World'})


@dajaxice_register(method='GET')
def get_my_hookups(request):
    my_shares = ShareGroup.objects.filter(owner=request.user)
    hookups = [share.hookup for share in my_shares]
    #objects = Hookup.objects.filter(id__in=hookup_ids)
    data = serializers.serialize("json", hookups)
    return data
