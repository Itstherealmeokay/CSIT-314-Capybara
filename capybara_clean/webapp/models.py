from django.db import models
from django.contrib.auth.models import AbstractUser

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

# Create your models here.
