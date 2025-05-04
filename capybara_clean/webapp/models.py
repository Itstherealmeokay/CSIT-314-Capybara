from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import django.utils.timezone
from datetime import datetime

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('homeowner', 'Homeowner'),
        ('cleaner', 'Cleaner'),
        ('platform_manager', 'Platform Manager'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

#Profile

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Homeowner(UserProfile):
    favourite_cleaners = models.ManyToManyField('Cleaner', related_name='favourite_cleaners', blank=True)
    favourite_listings = models.ManyToManyField('CleaningListing', related_name='favourite_listings', blank=True)

class Cleaner(UserProfile):
    pass

class PlatformManager(UserProfile):
    pass

class Property(models.Model):
    homeowner = models.ForeignKey(Homeowner, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name} - {self.address}'
    
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.name

class CleaningListingStatus(models.TextChoices):
    OPEN = 'open'
    CLOSED = 'closed'

class CleaningListing(models.Model):
    cleaner = models.ForeignKey(Cleaner, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(default=django.utils.timezone.now)
    date_closed = models.DateTimeField(null=True)
    price = models.FloatField()
    status = models.CharField(max_length=20, choices=CleaningListingStatus.choices, default=CleaningListingStatus.OPEN)
    rating = models.FloatField(null=True, default=None)

    def __str__(self):
        return f'{self.cleaner.full_name} - {self.service_category} [{self.price}] ({self.status})'
    
class CleaningListingView(models.Model):
    cleaning_listing = models.ForeignKey(CleaningListing, on_delete=models.CASCADE)
    date_viewed = models.DateTimeField(default=django.utils.timezone.now)
    homeowner = models.ForeignKey(Homeowner, on_delete=models.SET_NULL, null=True)
    
class CleaningRequestStatus(models.TextChoices):
    PENDING_CLEANER_ACCEPT = 'pending_cleaner_accept'
    PENDING_CLEANING = 'pending_cleaning'
    PENDING_REVIEW = 'pending_review'
    DECLINED = 'declined'
    COMPLETED = 'completed'

class CleaningRequest(models.Model):
    cleaning_listing = models.ForeignKey(CleaningListing, on_delete=models.SET_NULL, null=True)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True)
    request_date = models.DateTimeField()
    status = models.CharField(max_length=40, choices=CleaningRequestStatus.choices, default=CleaningRequestStatus.PENDING_CLEANER_ACCEPT)
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

