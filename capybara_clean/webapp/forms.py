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
        
from django import forms
from .models import CustomUser

class AdminUserEditForm(forms.ModelForm):
    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['username']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


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
        widgets = {
            'request_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        homeowner = kwargs.pop('homeowner')  # Get the user from the view
        super().__init__(*args, **kwargs)
        self.fields['property'].queryset = Property.objects.filter(homeowner=homeowner)

class CleaningRequestReviewForm(forms.ModelForm):
    class Meta:
        model = CleaningRequest
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'feedback': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your feedback...'}),
        }

class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name']
