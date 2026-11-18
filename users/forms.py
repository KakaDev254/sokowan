from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-custom py-2', 
            'placeholder': 'example@email.com'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-custom py-2', 
                'placeholder': 'Choose a username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control form-control-custom py-2', 
                'placeholder': 'John'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control form-control-custom py-2', 
                'placeholder': 'Doe'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-custom py-2', 
            'placeholder': '••••••••'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-custom py-2', 
            'placeholder': '••••••••'
        })


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes for the input-group icon layout
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-custom border-start-0 py-2', 
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control form-control-custom border-start-0 py-2', 
            'placeholder': 'Enter your password'
        })