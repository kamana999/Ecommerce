from django import forms
from shop.models import *


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'enter code here'
    }))


class CheckOutForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ("city", "state", "pin", "landmark", "contact", "alternative_no","name", "address_type", "default")


class AddReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("comment", "rating")

