from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class PriceSearchForm(forms.Form):
        date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
        date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))