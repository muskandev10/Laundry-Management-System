from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import LaundryOrder


class SignUpForm(UserCreationForm):
    """Extended user registration form with first/last name and email."""

    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'form-input',
            'id': 'signup-first-name',
            'autocomplete': 'off',
        }),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'form-input',
            'id': 'signup-last-name',
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'form-input',
            'id': 'signup-email',
        }),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-input',
            'id': 'signup-password1',
        }),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-input',
            'id': 'signup-password2',
        }),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
                'class': 'form-input',
                'id': 'signup-username',
            }),
        }


class LoginForm(forms.Form):
    """Simple login form."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or Email',
            'class': 'form-input',
            'id': 'login-username',

        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-input',
            'id': 'login-password',
        }),
    )


class LaundryRequestForm(forms.ModelForm):
    """Form for submitting a laundry service request."""

    class Meta:
        model = LaundryOrder
        fields = [
            'full_name', 'mobile', 'state', 'city', 'pin_code', 'address',
            'laundry_type', 'cloth_type', 'weight', 'description',
            'issued_date', 'delivery_date',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Enter your full name',
                'class': 'form-input',
                'id': 'request-fullname',
            }),
            'mobile': forms.TextInput(attrs={
                'placeholder': 'Enter mobile number',
                'class': 'form-input',
                'maxlength': '10',
                'id': 'request-mobile',
            }),
            'state': forms.Select(attrs={
                'class': 'form-select',
                'id': 'request-state',
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'Enter city',
                'class': 'form-input',
                'id': 'request-city',
            }),
            'pin_code': forms.TextInput(attrs={
                'placeholder': 'Enter pin code',
                'class': 'form-input',
                'maxlength': '6',
                'id': 'request-pincode',
            }),
            'address': forms.Textarea(attrs={
                'placeholder': 'Enter full address',
                'class': 'form-textarea',
                'rows': 3,
                'id': 'request-address',
            }),
            'laundry_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'request-laundry-type',
            }),
            'cloth_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'request-cloth-type',
            }),
            'weight': forms.NumberInput(attrs={
                'placeholder': 'Weight in KG',
                'class': 'form-input',
                'id': 'request-weight',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Any special instructions',
                'class': 'form-textarea',
                'rows': 3,
                'id': 'request-description',
            }),
            'issued_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'id': 'request-issued-date',
            }),
            'delivery_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'id': 'request-delivery-date',
            }),
        }


class TrackingForm(forms.Form):
    """Form for looking up order status by tracking ID."""

    tracking_id = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter Tracking ID',
            'class': 'form-input',
            'id': 'track-id-input',
        }),
    )


class AdminLoginForm(forms.Form):
    """Admin login form."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Admin Username',
            'class': 'form-input',
            'id': 'admin-login-username',
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-input',
            'id': 'admin-login-password',
        }),
    )
