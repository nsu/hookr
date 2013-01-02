from exchange.models import *
from django.forms import ModelForm
from django import forms
from django.db.models import Q
from django.forms.widgets import CheckboxSelectMultiple, TextInput, Select
from django.contrib.auth.models import User

class NumberInput(TextInput):
    input_type = 'number'

class HookupForm(ModelForm):
    #adding overridden initialization field, restrict categories to the ones with the user as the author 
    class Meta:
        model = Hookup
        fields = ('hookers',)      
        widgets = {
                   'hookers' : CheckboxSelectMultiple,
                   }   
    def __init__(self, network, *args, **kwargs):
        super(HookupForm, self).__init__(*args, **kwargs) 
        self.fields['hookers'].queryset = HookrProfile.objects.filter(network=network)
    def clean(self):
        cleaned_data = super(HookupForm, self).clean()
        hookers = cleaned_data.get("hookers")
        if(len(hookers)!=2):
            raise forms.ValidationError("Only hookups between two people can be traded")
        return cleaned_data
        
class BuyOrderForm(ModelForm):
    #adding overridden initialization field
    class Meta:
        model = BuyOrder
        fields = ('hookup','volume','price')      
        widgets = {
                   'hookup' : Select,
                   'price' : NumberInput,
                   'volume' : NumberInput,
                   }   
    def __init__(self, network, *args, **kwargs):
        super(BuyOrderForm, self).__init__(*args, **kwargs) 
        self.fields['hookup'].queryset = Hookup.objects.filter(network=network)
    def clean(self):
        cleaned_data = super(BuyOrderForm, self).clean()
        hookup = cleaned_data.get("hookup")
        price = cleaned_data.get("price")
        volume = cleaned_data.get("volume")
        return cleaned_data
        
class IPOOrderForm(ModelForm):
    #adding overridden initialization field
    class Meta:
        model = IPOOrder
        fields = ('hookup','volume',)      
        widgets = {
                   'hookup' : Select,
                   'volume' : NumberInput,
                   }   
    def __init__(self, network, *args, **kwargs):
        super(IPOOrderForm, self).__init__(*args, **kwargs) 
        self.fields['hookup'].queryset = PotentialIPO.objects.filter(network=network)
    def clean(self):
        cleaned_data = super(IPOOrderForm, self).clean()
        hookup = cleaned_data.get("hookup")
        volume = cleaned_data.get("volume")
        return cleaned_data
