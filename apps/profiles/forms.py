from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field_name


class ProfileEditForm(forms.ModelForm):
    birthday = forms.DateField(
        widget=forms.DateInput(format="%m/%d/%Y",
                               attrs={'placeholder': 'MM/DD/YYYY', 'class': 'form-control date-input'}),
        required=False
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name',
            'handicap', 'birthday', 'location', 'years_of_experience', 'creation_time', 'photo',
        )

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['first_name'].required = self.fields['last_name'].required = True
        self.fields['birthday'].widget.attrs['class'] = 'form-control date-input'
