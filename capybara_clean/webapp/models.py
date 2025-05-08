from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import django.utils.timezone
from datetime import datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect,render
from django.contrib.auth import authenticate
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('homeowner', 'Homeowner'),
        ('cleaner', 'Cleaner'),
        ('platform_manager', 'Platform Manager'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_suspended = models.BooleanField(default=False)
    
    def is_eligible_for_login(self):
        if self.is_suspended:
            return False, "Your account has been suspended."
        return True, None
    
    def get_dashboard_url(self):
        if self.is_staff:
            return reverse('admin:index')
        elif self.role == 'homeowner':
            return reverse('dashboard')  # Dashboard view auto-routes by role
        elif self.role == 'cleaner':
            return reverse('dashboard')
        elif self.role == 'platform_manager':
            return reverse('dashboard')
        else:
            return reverse('login')

    @classmethod
    def authenticate_user(cls, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            eligible, reason = user.is_eligible_for_login()
            if not eligible:
                return None, reason
            return user, None
        return None, "Invalid username or password."
    

#Profile

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_profile_info(self, request):
        profile,_= UserProfile.objects.get_or_create(user = request.user)
        properties = None
        if Homeowner.objects.filter(user=request.user).exists():
            properties = Property.objects.filter(homeowner__user=request.user)
        return {
            'profile': profile,
            'properties': properties,
        }

class ViewDashboard(models.Model):
    def get_dash(self, request):
        user = request.user
        if user.role == 'homeowner':
            dash = Homeowner.objects.get(user=user).get_dashboard_data(request)
            return {'user': user, 'dash': dash}
        elif user.role == 'cleaner':
            return Cleaner.objects.get(user=user).get_dashboard_data()        
        elif user.role == 'platform_manager':
            return PlatformManager.objects.get(user=user).get_dashboard_data()  
    
class Homeowner(UserProfile):
    favourite_cleaners = models.ManyToManyField('Cleaner', related_name='favourite_cleaners', blank=True)
    favourite_listings = models.ManyToManyField('CleaningListing', related_name='favourite_listings', blank=True)

    def get_dashboard_data(self, request):
        properties = Property.objects.filter(homeowner=self)
        property_data = []

        for property in properties:
            all_requests = property.cleaning_requests.all().order_by('-request_date')
            page_number = request.GET.get(f'page_{property.id}', 1)
            paginator = Paginator(all_requests, 3)
            page_obj = paginator.get_page(page_number)
            property_data.append({
                'property': property,
                'requests': page_obj
            })

        num_notifications = CleaningRequest.objects.filter(
            property__homeowner=self,
            status=CleaningRequestStatus.PENDING_REVIEW
        ).count()

        return {
            'property_data': property_data,
            'num_notifications': num_notifications
        }
    
    
    @classmethod
    def get_homeowner(cls, request):
        return cls.objects.get(user=request.user)
    
    def is_cleaner_favourited(self,cleaner):
        return self.favourite_cleaners.filter(pk=cleaner.pk).exists()
    
    def toggle_favourite_cleaner(self, cleaner):
        if self.is_cleaner_favourited(cleaner):
            self.favourite_cleaners.remove(cleaner)
            return False
        else:
            self.favourite_cleaners.add(cleaner)
            return True
    
    def get_cleaner_profile_data(self, cleaner_pk):
        cleaner = get_object_or_404(Cleaner, pk=cleaner_pk)
        is_favourited = self.is_cleaner_favourited(cleaner)
        return {
            'cleaner': cleaner,
            'is_favourited': is_favourited
        }
        
    def update_cleaner_favourite(self, cleaner_pk):
        cleaner = get_object_or_404(Cleaner, pk=cleaner_pk)
        is_favourited = self.toggle_favourite_cleaner(cleaner)
        return {
            'cleaner': cleaner,
            'is_favourited': is_favourited
        }
    @classmethod
    def is_homeowner(cls, request):
        if request.user.role == 'homeowner':
            return 'webapp/property_create.html'
        else:
            return 'webapp/view_profile.html'
        
    @staticmethod
    def create_property_from_post(request):
        if request.user.role != 'homeowner':
            return redirect('view_profile')
        from .forms import PropertyForm
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.homeowner = Homeowner.objects.get(user=request.user)
            property.save()
            return redirect('view_profile')  # redirect to prevent duplicate submission

        # On error, return render
        return render(request, 'webapp/property_create.html', {'form': form})
    
    @classmethod
    def delete_property_by_id(cls, request, property_id):
        homeowner = cls.objects.get(user=request.user)
        property = get_object_or_404(Property, id=property_id, homeowner=homeowner)
        property.delete()
        
    @classmethod
    def get_property_update_form(cls, request, property_id):
        from .forms import PropertyForm
        homeowner = cls.objects.get(user=request.user)
        property = get_object_or_404(Property, id=property_id, homeowner=homeowner)
        form = PropertyForm(instance=property)
        return 'webapp/property_update.html', {'form': form}

    @classmethod
    def update_property_from_post(cls, request, property_id):
        from .forms import PropertyForm
        homeowner = cls.objects.get(user=request.user)
        property = get_object_or_404(Property, id=property_id, homeowner=homeowner)
        form = PropertyForm(request.POST, instance=property)

        if form.is_valid():
            form.save()
            dashboard_data = homeowner.get_dashboard_data(request)
            dashboard_data['profile'] = homeowner
            dashboard_data['properties'] = Property.objects.filter(homeowner=homeowner)
            return 'webapp/view_profile.html', dashboard_data

        return 'webapp/property_update.html', {'form': form}
    
    @classmethod
    def get_cleaner_browser_data(cls, request):
        homeowner = cls.objects.get(user=request.user)
        query = request.GET.get('q', '').strip()
        fav_query = request.GET.get('fq', '').strip()

        cleaners = Cleaner.objects.all()
        favourite_cleaners = homeowner.favourite_cleaners.all()

        if query:
            cleaners = cleaners.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(full_name__icontains=query)
            )

        if fav_query:
            favourite_cleaners = favourite_cleaners.filter(
                Q(user__first_name__icontains=fav_query) |
                Q(user__last_name__icontains=fav_query) |
                Q(full_name__icontains=fav_query)
            )

        paginator = Paginator(cleaners, 8)
        page_number = request.GET.get('page')
        
        try:
            cleaners_page = paginator.page(page_number)
        except PageNotAnInteger:
            cleaners_page = paginator.page(1)
        except EmptyPage:
            cleaners_page = paginator.page(paginator.num_pages)

        context = {
            'cleaners': cleaners_page,
            'query': query,
            'favourite_cleaners': favourite_cleaners,
            'favourite_query': fav_query
        }

        return 'webapp/browsecleaners.html', context

    @classmethod
    def handle_cleaner_favourite_removal(cls, request):
        homeowner = cls.objects.get(user=request.user)
        cleaner_id = request.POST.get('cleaner_id')

        if cleaner_id:
            cleaner = Cleaner.objects.filter(id=cleaner_id).first()
            if cleaner:
                homeowner.favourite_cleaners.remove(cleaner)

        return cls.get_cleaner_browser_data(request)



class Cleaner(UserProfile):
     def get_dashboard_data(self):
        listings = self.cleaning_listings.all()
        listing_data = [{
            'listing': listing,
            'requests': listing.requests.all()
        } for listing in listings]

        num_notifications = CleaningRequest.objects.filter(
            cleaning_listing__cleaner=self
        ).filter(
            Q(status=CleaningRequestStatus.PENDING_CLEANER_ACCEPT) |
            Q(status=CleaningRequestStatus.PENDING_CLEANING)
        ).count()

        return {
            'listing_data': listing_data,
            'num_notifications': num_notifications
        }

class PlatformManager(UserProfile):  # or whatever base class you use
    def get_dashboard_data(self):
        def get_cleaner_stats(start_date: datetime):
            return [{
                'cleaner': cleaner,
                'num_requests': CleaningRequest.objects.filter(
                    Q(request_date__date__gte=start_date) & Q(cleaning_listing__cleaner=cleaner)
                ).count(),
                'views': CleaningListingView.objects.filter(
                    Q(date_viewed__date__gte=start_date) & Q(cleaning_listing__cleaner=cleaner)
                ).count(),
            } for cleaner in Cleaner.objects.all()]

        start_of_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_cleaner_stats = get_cleaner_stats(start_of_today)
        monthly_cleaner_stats = get_cleaner_stats(start_of_today.replace(day=1))
        yearly_cleaner_stats = get_cleaner_stats(start_of_today.replace(month=1, day=1))

        return {
            'new_users': CustomUser.objects.order_by('-date_joined')[:3],
            'overall_stats': {
                'cleaner': {
                    'users': Cleaner.objects.count(),
                    'listings': CleaningListing.objects.count(),
                    'requests': CleaningRequest.objects.count(),
                },
                'homeowner': {
                    'users': Homeowner.objects.count(),
                    'properties': Property.objects.count(),
                },
            },
            'reports': {
                'daily': {
                    'registrations': CustomUser.objects.filter(date_joined__date=start_of_today).count(),
                    'top_3_viewed': sorted(daily_cleaner_stats, key=lambda cleaner: cleaner['views'], reverse=True)[:3],
                    'top_3_requested': sorted(daily_cleaner_stats, key=lambda cleaner: cleaner['num_requests'], reverse=True)[:3],
                },
                'monthly': {
                    'registrations': CustomUser.objects.filter(date_joined__date__gte=start_of_today.replace(day=1)).count(),
                    'top_3_viewed': sorted(monthly_cleaner_stats, key=lambda cleaner: cleaner['views'], reverse=True)[:3],
                    'top_3_requested': sorted(monthly_cleaner_stats, key=lambda cleaner: cleaner['num_requests'], reverse=True)[:3],
                },
                'yearly': {
                    'registrations': CustomUser.objects.filter(date_joined__date__gte=start_of_today.replace(month=1, day=1)).count(),
                    'top_3_viewed': sorted(yearly_cleaner_stats, key=lambda cleaner: cleaner['views'], reverse=True)[:3],
                    'top_3_requested': sorted(yearly_cleaner_stats, key=lambda cleaner: cleaner['num_requests'], reverse=True)[:3],
                },
            },
        }

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
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE, null=True, related_name='cleaning_listings')
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





from django.db import models
from django.db.models import Q

class CleaningRequest(models.Model):
    cleaning_listing = models.ForeignKey(CleaningListing, on_delete=models.CASCADE, null=True, related_name='requests')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, related_name='cleaning_requests')
    request_date = models.DateTimeField()
    status = models.CharField(max_length=40, choices=CleaningRequestStatus.choices, default=CleaningRequestStatus.PENDING_CLEANER_ACCEPT)
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.cleaning_listing.name} on {self.property.address} - {self.status}'

    @classmethod
    def get_filtered_requests(cls, request):
        user = request.user
        search_query = request.GET.get('search')
        queryset = cls.objects.filter(property__homeowner__user=user)
        if search_query:
            queryset = queryset.filter(
                Q(cleaning_listing__cleaner__full_name__icontains=search_query) |
                Q(cleaning_listing__name__icontains=search_query) |
                Q(request_date__icontains=search_query) |
                Q(status__icontains=search_query)
            )
        return queryset.order_by('-request_date'), search_query


