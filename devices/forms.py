from django import forms

class AngleScan(forms.Form):
    count = forms.CharField(min_length=1, max_length=2)
