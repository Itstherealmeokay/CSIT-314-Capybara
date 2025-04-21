from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('homeowner', 'Homeowner'),
        ('cleaner', 'Cleaner'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

#Profile

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Homeowner(UserProfile):
    properties = models.ManyToManyField('Property', related_name='homeowners', blank=True) 

class Cleaner(UserProfile):
    cleaning_requests = models.ManyToManyField('CleaningRequest', related_name='cleaners', blank=True)

class Property(models.Model):
    address = models.CharField(max_length=200)
    property_type = models.CharField(max_length=100)
    
class CleaningRequest(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE)
    request_date = models.DateTimeField()
    description = models.TextField()
    status = models.CharField(max_length=20)

