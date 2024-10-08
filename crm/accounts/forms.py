# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import CustomUser, Company,  Area

class CustomUserCreationForm(UserCreationForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False)
    
    class Meta:
        model = CustomUser
        fields = ('mobile', 'email', 'company', 'user_type')

class CustomUserChangeForm(UserChangeForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False)
    
    class Meta:
        model = CustomUser
        fields = ('mobile', 'email', 'company', 'user_type')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Mobile Number",
        widget=forms.TextInput(attrs={'autofocus': True}),
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Mobile number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter mobile number'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter password'})

