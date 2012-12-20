from exchange.models import Hookup, HookrProfile, Network, IPOOrder, PotentialIPO
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
        
class IPOForm(ModelForm):
    #adding overridden initialization field, restrict categories to the ones with the user as the author 
    class Meta:
        model = IPOOrder
        fields = ('hookup','volume',)      
        widgets = {
                   'hookup' : Select,
                   'volume' : NumberInput,
                   }   
    def __init__(self, network, *args, **kwargs):
        super(IPOForm, self).__init__(*args, **kwargs) 
        self.fields['hookup'].queryset = PotentialIPO.objects.filter(network=network)
    def clean(self):
        cleaned_data = super(IPOForm, self).clean()
        hookup = cleaned_data.get("hookup")
        volume = cleaned_data.get("volume")
        return cleaned_data
