from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import django.utils.timezone
from datetime import datetime
from django.db.models import Q, Avg
from django.shortcuts import get_object_or_404, redirect,render
from django.contrib.auth import authenticate
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('homeowner', 'Homeowner'),
        ('cleaner', 'Cleaner'),
        ('platform_manager', 'Platform Manager'),
        ('adminuser', 'Admin User'),
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
        elif self.role == 'adminuser':
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
    is_suspended = models.BooleanField(default=False)
    
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
        
    @classmethod
    def get_edit_context(cls, request):
        from .forms import UserProfileForm
        profile, _ = cls.objects.get_or_create(user=request.user)
        form = UserProfileForm(instance=profile)
        return {
            'form': form
        }
        

    @classmethod
    def handle_edit_submission(cls, request):
        from .forms import UserProfileForm
        profile, _ = cls.objects.get_or_create(user=request.user)
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return True, None
        return False, {
            'form': form
        }
        
    @classmethod
    def get_admin_edit_context(cls, user_id):
        from .forms import UserProfileForm
        user = get_object_or_404(CustomUser, id=user_id)
        profile, _ = cls.objects.get_or_create(user=user)
        form = UserProfileForm(instance=profile)
        return {
            'form': form,
            'editing_user': user
        }

    @classmethod
    def handle_admin_edit_submission(cls, request, user_id):
        from .forms import UserProfileForm
        user = get_object_or_404(CustomUser, id=user_id)
        profile, _ = cls.objects.get_or_create(user=user)
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return True, None
        return False, {
            'form': form,
            'editing_user': user
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
        elif user.role == 'adminuser':
            return AdminUser.objects.get(user=user).get_dashboard_data(request)  
    
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class AdminUser(UserProfile):
    @classmethod
    def get_dashboard_data(cls, request):
        query = request.GET.get('q', '')
        all_users = UserProfile.objects.all()  # Fetch all users
        all_users = all_users.exclude(user__role='admin')
        
        if query:
            all_users = all_users.filter(
                Q(full_name__icontains=query) |
                Q(user__username__icontains=query)
            )
        
        # Pagination logic
        page_number = request.GET.get('page', 1)  # Get page number from the request
        paginator = Paginator(all_users, 5)  # Show 10 users per page
        
        try:
            page_obj = paginator.page(page_number)  # Get the page object
        except PageNotAnInteger:
            page_obj = paginator.page(1)  # If page is not an integer, show the first page
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)  # If page is out of range, show last page
        
        return {
            'all_users': page_obj,  # Return the paginated result
            'query': query
        }
        
    @classmethod
    def get_user_account_form(cls, user_id):
        from .forms import AdminUserEditForm
        user = CustomUser.objects.get(id=user_id)
        form = AdminUserEditForm(instance=user)
        return form, user

    @classmethod
    def save_user_account_form(cls, request, user_id):
        from .forms import AdminUserEditForm
        user = CustomUser.objects.get(id=user_id)
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            password1 = form.cleaned_data.get('password1')
            if password1:
                updated_user.set_password(password1)
            updated_user.save()
            return True, None  # success
        return False, form  # failed, return form with errors
    
    @classmethod
    def toggle_suspension(cls, user_id):
        user = CustomUser.objects.get(id=user_id)
        user.is_suspended = not user.is_suspended
        user.save()
        return user.is_suspended
    
    @classmethod
    def toggle_suspension_profile(cls, user_id):
        user = UserProfile.objects.get(id=user_id)
        user.is_suspended = not user.is_suspended
        user.save()
        return user.is_suspended
    
    @classmethod
    def search_users(cls, request, role=None):
        from webapp.models import Homeowner, Cleaner, PlatformManager, AdminUser, UserProfile

        query = request.GET.get('q', '').strip()
        page_number = request.GET.get('page')

        if role == 'homeowner':
            users = Homeowner.objects.select_related('user')
        elif role == 'cleaner':
            users = Cleaner.objects.select_related('user')
        elif role == 'platform_manager':
            users = PlatformManager.objects.select_related('user')
        elif role == 'adminuser':
            users = AdminUser.objects.select_related('user')
        else:
            users = UserProfile.objects.select_related('user')  # fallback

        if query:
            users = users.filter(
                Q(user__email__icontains=query) |
                Q(user__username__icontains=query) |
                Q(full_name__icontains=query) |
                Q(phone_number__icontains=query)
            )

        paginator = Paginator(users, 10)
        page_obj = paginator.get_page(page_number)

        return {
            'query': query,
            'role': role,
            'page_obj': page_obj,
            'users': page_obj.object_list,
        }
        
    @classmethod
    def get_admin_view_context(cls, user_id):
        users = UserProfile.objects.get(id=user_id)
        return {'users': users}
    
    @classmethod
    def get_admin_viewaccount_context(cls, user_id):
        from .forms import AdminUserEditForm
        user_account = CustomUser.objects.get(id=user_id)
        return {'user_account': user_account}
    
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
    
    @classmethod
    def get_create_context(cls, request):
        from .forms import ServiceCategoryForm
        if request.user.role != 'platform_manager':
            return {'redirect': 'dashboard'}
        return {'form': ServiceCategoryForm()}

    @classmethod
    def handle_create_submission(cls, request):
        if request.user.role != 'platform_manager':
            return {'redirect': 'dashboard'}
        from .forms import ServiceCategoryForm
        from django.contrib import messages
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if cls.objects.filter(name=name).exists():
                messages.error(request, 'Service category already exists.')
            else:
                form.save()
                messages.success(request, 'Service category added successfully.')
                return {'redirect': 'service_category_view'}
        return {'form': form}
    
    @classmethod
    def get_list_context(cls):
        return {'categories': cls.objects.all()}

    @classmethod
    def handle_delete(cls, request, category_id):
        if request.user.role != 'platform_manager':
            return {'redirect': 'dashboard'}

        category = get_object_or_404(cls, id=category_id)
        category.delete()
        return {'redirect': 'service_category_view'}
    
    @classmethod
    def handle_update(cls, request, category_id):
        if request.user.role != 'platform_manager':
            return {'redirect': 'dashboard'}

        category = get_object_or_404(cls, id=category_id)
        from .forms import ServiceCategoryForm
        from django.contrib import messages
        form = ServiceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service category updated successfully.')
            return {'redirect': 'service_category_view'}
        return {'form': form}
    

    @classmethod
    def search(cls, request):
        query = request.GET.get('q', '').strip()
        all_categories = cls.objects.filter(name__icontains=query) if query else cls.objects.all()

        paginator = Paginator(all_categories, 3)  # Show 3 per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return {
            'categories': page_obj.object_list,
            'query': query,
            'page_obj': page_obj,
        }


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
    
    @classmethod
    def get_browse_context(cls, request):
        if request.user.role not in ('homeowner', 'cleaner'):
            return {'redirect': 'dashboard'}

        query = request.GET.get('q')
        page = request.GET.get('page')

        listings = cls._filter_listings(query)
        enriched = cls._add_metadata(listings)
        paginated = cls._paginate(enriched, page)

        context = {
            "listings": paginated,
            "query": query,
            "page": page,
        }

        if request.user.role == 'homeowner':
            homeowner = Homeowner.objects.get(user=request.user)
            favourite_listings = homeowner.favourite_listings.all()
            favourite_data = cls._add_metadata(favourite_listings)
            context['favourite_listings'] = favourite_data

        return context


    @classmethod
    def _filter_listings(cls, query):
        if query:
            query = query.strip()
            return cls.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(service_category__name__icontains=query)
            )
        return cls.objects.all()

    @classmethod
    def _add_metadata(cls, listings):
        return [{
            'listing': listing,
            'views': listing.view_count(),
            'rating': listing.average_rating(),
        } for listing in listings]

    @classmethod
    def _paginate(cls, listings, page_number):
        paginator = Paginator(listings, 8)
        try:
            return paginator.page(page_number)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    def view_count(self):
        return self.cleaninglistingview_set.count()

    def average_rating(self):
        return self.requests.aggregate(Avg('rating'))['rating__avg']
    
    def get_detail_context_for_user(self, user):
        is_favourited = False
        if user.role == 'homeowner':
            homeowner = Homeowner.objects.get(user=user)
            CleaningListingView.objects.create(cleaning_listing=self, homeowner=homeowner)
            is_favourited = homeowner.favourite_listings.filter(id=self.id).exists()
        
        return {
            'listing': self,
            'belongs_to_user': user == self.cleaner.user,
            'is_homeowner_favourited': is_favourited,
    }
        
    @classmethod
    def get_create_context(cls, request):
        from .forms import CleaningListingForm
        if request.user.role != 'cleaner':
            return {'redirect': 'dashboard'}
        return {'form': CleaningListingForm()}

    @classmethod
    def create_from_request(cls, request):
        from .forms import CleaningListingForm
        if request.user.role != 'cleaner':
            return {'redirect': 'dashboard'}

        form = CleaningListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.cleaner = Cleaner.objects.get(user=request.user)
            listing.save()
            return {'redirect': 'cleaning_listings_browse'}
        
        return {'form': form}
    
    @classmethod
    def get_home_view_listing_context(cls, cleaner_pk):
        cleaner = get_object_or_404(Cleaner, pk=cleaner_pk)
        listings = cls.objects.filter(cleaner=cleaner)
        return {
            'cleaner': cleaner,
            'listings': listings,
        }



    @classmethod
    def get_update_context(cls, request, listing_id):
        from .forms import CleaningListingForm
        listing = get_object_or_404(cls, id=listing_id)
        form = CleaningListingForm(instance=listing)
        return {'form': form}

    @classmethod
    def post_update_context(cls, request, listing_id):
        from .forms import CleaningListingForm
        listing = get_object_or_404(cls, id=listing_id)
        form = CleaningListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            return {'redirect': 'cleaning_listings_browse'}
        return {'form': form}

    @classmethod
    def handle_favourite_action(cls, request, listing_id):
        listing = get_object_or_404(cls, id=listing_id)
        user = request.user

        if user.role != 'homeowner':
            return {'redirect': 'cleaning_listings_view', 'listing_id': listing_id}

        homeowner = Homeowner.objects.get(user=user)
        action = 'add_favourite' in request.POST

        if action:
            homeowner.favourite_listings.add(listing)
        else:
            homeowner.favourite_listings.remove(listing)

        redirect_url = request.POST.get('redirect') or 'cleaning_listings_browse'
        return {'redirect': redirect_url}
    
    @classmethod
    def get_application_context(cls, request, listing_id):
        if request.user.role != 'homeowner':
            return {'redirect': 'cleaning_listings_view', 'listing_id': listing_id}

        from .forms import CleaningRequestForm
        listing = cls.objects.get(id=listing_id)
        homeowner = Homeowner.objects.get(user=request.user)

        return {
            'listing_id': listing_id,
            'form': CleaningRequestForm(homeowner=homeowner)
        }

    @classmethod
    def process_application_post(cls, request, listing_id):
        if request.user.role != 'homeowner':
            return {'redirect': 'cleaning_listings_view', 'listing_id': listing_id}

        listing = cls.objects.get(id=listing_id)
        homeowner = Homeowner.objects.get(user=request.user)

        from .forms import CleaningRequestForm
        form = CleaningRequestForm(request.POST, homeowner=homeowner)
        if form.is_valid():
            cleaning_request = form.save(commit=False)
            cleaning_request.cleaning_listing = listing
            cleaning_request.save()
            return {'redirect': 'cleaning_listings_browse'}

        return {
            'listing_id': listing_id,
            'form': form
        }
    @classmethod
    def handle_delete(cls, request, listing_id):
        listing = get_object_or_404(cls, id=listing_id)
        # Optional: Add ownership check here if needed
        listing.delete()
        return 'cleaning_listings_browse'

    
    
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
    
    @classmethod
    def get_cleaner_filtered_requests(cls, request):
        user = request.user
        search_query = request.GET.get('search')
        queryset = cls.objects.filter(cleaning_listing__cleaner__user=user)
        if search_query:
            queryset = queryset.filter(
                Q(cleaning_listing__name__icontains=search_query) |
                Q(request_date__icontains=search_query) |
                Q(status__icontains=search_query)
            )
        return queryset.order_by('-request_date'), search_query


