from django import forms


class CompareAddProductForm(forms.Form):
    update = forms.BooleanField(required=False,
        initial=False,widget=forms.HiddenInput)