from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('homeowner', 'Homeowner'),
        ('cleaner', 'Cleaner'),
        
        
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_homeowner(self):
        return self.role == 'homeowner'
    
    def is_cleaner(self):
        return self.role == 'cleaner'

#Profile

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"