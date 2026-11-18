from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control rounded-pill mb-3', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control rounded-pill mb-3', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control rounded-pill mb-3', 'placeholder': 'Phone Number (e.g., 0712345678)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill mb-3', 'placeholder': 'Email (Optional)'}),
            'address': forms.TextInput(attrs={'class': 'form-control rounded-pill mb-3', 'placeholder': 'Delivery Address (e.g., Building, Street)'}),
            'city': forms.TextInput(attrs={'class': 'form-control rounded-pill mb-3', 'placeholder': 'City / Estate (e.g., Westlands, Nairobi)'}),
        }