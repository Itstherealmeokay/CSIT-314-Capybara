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
    email_address = models.CharField(max_length=200, null=True , blank=True)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Homeowner(UserProfile):
    properties = models.ManyToManyField('Property', related_name='homeowners', blank=True)
    favourite_cleaners = models.ManyToManyField('Cleaner', related_name='favourite_cleaners', blank=True)

class Cleaner(UserProfile):
    cleaning_requests = models.ManyToManyField('CleaningRequest', related_name='cleaners', blank=True)

class Property(models.Model):
    address = models.CharField(max_length=200)
    property_type = models.CharField(max_length=100)

class ServiceCategory(models.Model):
    pass
class CleaningListing(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    price = models.FloatField()
    status = models.CharField(max_length=20)
    
class CleaningRequest(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE)
    request_date = models.DateTimeField()
    description = models.TextField()
    status = models.CharField(max_length=20)

