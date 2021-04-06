from django import forms

from billing.models import BillingInfo
from core.utils import get_country_list


class BillingForm(forms.ModelForm):
    country = forms.ChoiceField(choices=get_country_list())
    stripe_token = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = BillingInfo
        fields = (
            'email', 'first_name', 'last_name',
            'address_line1', 'address_line2', 'postcode', 'state', 'city',
            'country', 'stripe_token'
        )
        required = (
            'email', 'first_name', 'last_name', 'address_line1', 'postcode', 'state', 'city', 'country', 'stripe_token'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in self.Meta.required:
                field.required = True
