from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from .models import *


class CreateUserForm(UserCreationForm):
    # TODO: Double check if you allow people to be admin from this
    role = forms.ChoiceField(
        label="What role are you registering as?",
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.RadioSelect,
    )
    class Meta:
        model = CustomUser  
        fields = ['username','password1', 'password2', 'role']
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'address', 'phone_number']

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'address']

class CleaningListingForm(forms.ModelForm):
    class Meta:
        model = CleaningListing
        fields = ['name', 'description', 'service_category', 'price']
        
class CleaningRequestForm(forms.ModelForm):
    class Meta:
        model = CleaningRequest
        fields = ['property', 'request_date']

class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name']
