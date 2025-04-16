from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from .models import CustomUser

class CreateUserForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)
    class Meta:
        model = CustomUser  
        fields = ['username','password1', 'password2', 'role']
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())