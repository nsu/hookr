from django.http import HttpResponse, HttpResponseRedirect
from django.forms import ModelForm
from exchange.forms import HookupForm
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
def get_hookup(request, network):
    network=Network.objects.get(name=network)
    if request.method == 'POST':
        #Create a new Example instance using the information contained in request.method is the method if POST
        newHookup = Hookup(network=network)                           #Build the form using an exist Example instance with the user as the author
        form = HookupForm(network, request.POST)
        if form.is_valid():                                                  #Save the Example to database if the form is valid then redirect current directory to home
            newHookup.save()        
            newHookup.hookers=form.cleaned_data['hookers']
            newHookup.save()
            return HttpResponse('True')
        else:
            return HttpResponse('False')
    else:
        form = HookupForm(network)
        return render(request, 'formTemplate.html',{                                #Render the request to formTemplate.html, map 'form' in the HTML file to the form variable in the view
            'form': form
        })
