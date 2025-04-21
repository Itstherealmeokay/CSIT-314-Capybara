from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from .models import CustomUser, UserProfile


class CreateUserForm(UserCreationForm):
    # TODO: Double check if you allow people to be admin from this
    role = forms.ChoiceField(label="What role are you registering as?", choices=CustomUser.ROLE_CHOICES)
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