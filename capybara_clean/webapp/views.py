from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from .forms import *
from .models import *


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'webapp/index.html')

class RegisterView(View):
    def get(self, request):
        return render(request, 'webapp/register.html', {'form': CreateUserForm()})
    
    def post(self, request):
        form = CreateUserForm(request.POST)
        if not form.is_valid():
            return render(request, 'webapp/register.html', {'form': form})
        user = form.save(commit=False)
        role = form.cleaned_data['role']
        user.role = role
        user.save()
        if role == 'homeowner':
            Homeowner.objects.create(user=user)
        elif role == 'cleaner':
            Cleaner.objects.create(user=user)
        elif role == 'platform_manager':
            PlatformManager.objects.create(user=user)
        return redirect('login')

def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {'form': form}
    return render(request, 'webapp/edit_profile.html', context)

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'webapp/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm()
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        return render(request, 'webapp/login.html', {'form': form})

class Dashboard(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        if request.user.is_staff:
            return self.admin_dashboard(request)
        if request.user.role == 'homeowner':
            return self.homeowner_dashboard(request)
        if request.user.role == 'cleaner':
            return self.cleaner_dashboard(request)
        if request.user.role == 'platform_manager':
            return self.platform_manager_dashboard(request)
        return redirect('login')
    
    def admin_dashboard(self, request):
        return redirect('/admin/')

    def homeowner_dashboard(self, request):
        properties = Property.objects.filter(homeowner=Homeowner.objects.get(user=request.user))
        property_data = [{
            'property': property,
            'requests': CleaningRequest.objects.filter(property=property),
        } for property in properties]
        num_notifications = CleaningRequest.objects.filter(
            property__homeowner__user=request.user
        ).filter(
            Q(status=CleaningRequestStatus.PENDING_REVIEW)
        ).count()
        return render(request, 'webapp/dashboard_homeowner.html', {
            'user': request.user,
            'property_data': property_data,
            'num_notifications': num_notifications,
        })
    
    def cleaner_dashboard(self, request):
        listings = CleaningListing.objects.filter(cleaner=Cleaner.objects.get(user=request.user))
        listing_data = [{
            'listing': listing,
            'requests': CleaningRequest.objects.filter(cleaning_listing=listing),
        } for listing in listings]
        num_notifications = CleaningRequest.objects.filter(
            cleaning_listing__cleaner=Cleaner.objects.get(user=request.user)
        ).filter(
            Q(status=CleaningRequestStatus.PENDING_CLEANER_ACCEPT) |
            Q(status=CleaningRequestStatus.PENDING_CLEANING)
        ).count()
        return render(request, 'webapp/dashboard_cleaner.html', {
            'user': request.user,
            'listing_data': listing_data,
            'num_notifications': num_notifications,
        })
    
    def platform_manager_dashboard(self, request):
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        
        daily_cleaner_stats = [{
            'cleaner': cleaner,
            'num_requests': CleaningRequest.objects.filter(
                Q(request_date__date=today) & Q(cleaning_listing__cleaner=cleaner)
            ).count(),
            'views': CleaningListingView.objects.filter(
                Q(date_viewed__date=today) & Q(cleaning_listing__cleaner=cleaner)
            ).count(),
        } for cleaner in Cleaner.objects.all()]
        monthly_cleaner_stats = [{
            'cleaner': cleaner,
            'num_requests': CleaningRequest.objects.filter(
                Q(request_date__date__gte=start_of_month) & Q(cleaning_listing__cleaner=cleaner)
            ).count(),
            'views': CleaningListingView.objects.filter(
                Q(date_viewed__date__gte=start_of_month) & Q(cleaning_listing__cleaner=cleaner)
            ).count(),
        } for cleaner in Cleaner.objects.all()]
        yearly_cleaner_stats = [{
            'cleaner': cleaner,
            'num_requests': CleaningRequest.objects.filter(
                Q(request_date__date__gte=start_of_year) & Q(cleaning_listing__cleaner=cleaner)
            ).count(),
            'views': CleaningListingView.objects.filter(
                Q(date_viewed__date__gte=start_of_year) & Q(cleaning_listing__cleaner=cleaner)
            ).count(),
        } for cleaner in Cleaner.objects.all()]
        
        data = {
            'user': request.user,
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
                    'registrations': CustomUser.objects.filter(date_joined__date=today).count(),
                    'top_3_viewed': sorted(daily_cleaner_stats, key=lambda cleaner: cleaner['views'])[-3:],
                    'top_3_requested': sorted(daily_cleaner_stats, key=lambda cleaner: cleaner['num_requests'])[-3:],
                },
                'monthly': {
                    'registrations': CustomUser.objects.filter(date_joined__date__gte=start_of_month).count(),
                    'top_3_viewed': sorted(monthly_cleaner_stats, key=lambda cleaner: cleaner['views'])[-3:],
                    'top_3_requested': sorted(monthly_cleaner_stats, key=lambda cleaner: cleaner['num_requests'])[-3:],
                },
                'yearly': {
                    'registrations': CustomUser.objects.filter(date_joined__date__gte=start_of_year).count(),
                    'top_3_viewed': sorted(yearly_cleaner_stats, key=lambda cleaner: cleaner['views'])[-3:],
                    'top_3_requested': sorted(yearly_cleaner_stats, key=lambda cleaner: cleaner['num_requests'])[-3:],
                },
            },
        }
        
        return render(request, 'webapp/dashboard_platformmanager.html', data)

@login_required(login_url='login')
def view_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    properties = None
    if Homeowner.objects.filter(user=request.user).exists():
        properties = Property.objects.filter(homeowner=Homeowner.objects.get(user=request.user))
    data = {
        'profile': profile,
        'properties': properties,
    }
    return render(request, 'webapp/view_profile.html', data)

class CleanerProfile(LoginRequiredMixin, View):
    def get(self, request, pk):
        cleaner = get_object_or_404(Cleaner, pk=pk)
        is_favourited = Homeowner.objects.get(user=request.user).favourite_cleaners.contains(cleaner)
        return render(request, 'webapp/cleaner_profile.html', {'cleaner': cleaner, 'is_favourited': is_favourited})
    
    def post(self, request, pk):
        favourite_cleaners = Homeowner.objects.get(user=request.user).favourite_cleaners
        cleaner = get_object_or_404(Cleaner, pk=pk)
        if favourite_cleaners.contains(cleaner):
            favourite_cleaners.remove(cleaner)
        else:
            favourite_cleaners.add(cleaner)
        is_favourited = favourite_cleaners.contains(cleaner)
        return render(request, 'webapp/cleaner_profile.html', {'cleaner': cleaner, 'is_favourited': is_favourited})

@login_required(login_url='login')
def property_create(request):
    if request.user.role != 'homeowner':
        return redirect('view_profile')

    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.homeowner = Homeowner.objects.get(user=request.user)
            property.save()
            return redirect('view_profile')
    else:
        form = PropertyForm()

    return render(request, 'webapp/property_create.html', {'form': form})

@login_required(login_url='login')
def property_update(request, property_id):
    property = Property.objects.get(id=property_id)
    if property.homeowner.user != request.user:
        return redirect('view_profile')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = PropertyForm(instance=property)

    return render(request, 'webapp/property_update.html', {'form': form})

@login_required(login_url='login')
def property_delete(request, property_id):
    property = Property.objects.get(id=property_id)
    if property.homeowner.user != request.user:
        return redirect('view_profile')
    property.delete()
    return redirect('view_profile')

@login_required(login_url='login')
def browse_cleaners(request):
    query = request.GET.get('q')
    homeowner = Homeowner.objects.get(user=request.user)
    cleaners = Cleaner.objects.all()
    favourite_cleaners = Homeowner.objects.get(user=request.user).favourite_cleaners.all()
    
    #remove from favourites
    if request.method == 'POST':
        cleaner_id = request.POST.get('cleaner_id')
        cleaner = Cleaner.objects.get(id=cleaner_id)
        homeowner.favourite_cleaners.remove(cleaner)
        return redirect('browsecleaners')

    if query:
        query = query.strip()
        cleaners = Cleaner.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(full_name__icontains=query) 
    )
        
    paginator = Paginator(cleaners, 8)
    page_number = request.GET.get('page')
    
    try:
        cleaners = paginator.page(page_number)
    except PageNotAnInteger:
        cleaners = paginator.page(1)
    except EmptyPage:
        cleaners = paginator.page(paginator.num_pages)

    return render(request, 'webapp/browsecleaners.html', {'cleaners': cleaners, 'query': query, 'favourite_cleaners': favourite_cleaners})

@login_required(login_url='login')
def cleaning_listings_browse(request):
    if request.user.role not in ('homeowner', 'cleaner'):
        return redirect('dashboard')  # prevent unauthorized access

    listings = CleaningListing.objects.all()
    return render(request, 'webapp/cleaning_listings_browse.html', {'listings': listings})

@login_required(login_url='login')
def cleaning_listing_view(request, listing_id):
    listing = get_object_or_404(CleaningListing, id=listing_id)
    listing.views += 1
    listing.save()
    data = {
        'listing': listing,
        'belongs_to_user': request.user == listing.cleaner.user
    }
    return render(request, 'webapp/cleaning_listing_view.html', data)

@login_required(login_url='login')
def cleaning_listing_create(request):
    if request.user.role != 'cleaner':
        return redirect('dashboard')

    if request.method == 'POST':
        form = CleaningListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.cleaner = Cleaner.objects.get(user=request.user)
            listing.save()
            return redirect('cleaning_listings_browse')
    else:
        form = CleaningListingForm()

    return render(request, 'webapp/cleaning_listing_create.html', {'form': form})

@login_required(login_url='login')
def cleaning_listing_update(request, listing_id):
    listing = get_object_or_404(CleaningListing, id=listing_id)
    if request.method == 'POST':
        form = CleaningListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('cleaning_listings_browse')
    else:
        form = CleaningListingForm(instance=listing)

    return render(request, 'webapp/cleaning_listing_update.html', {'form': form})

@login_required(login_url='login')
def cleaning_listing_apply(request, listing_id):
    if request.user.role != 'homeowner':
        return redirect('cleaning_listings_view', listing_id)
    
    cleaning_listing = CleaningListing.objects.get(id=listing_id)
    homeowner = Homeowner.objects.get(user=request.user)
    if request.method == 'POST':
        form = CleaningRequestForm(request.POST, homeowner=homeowner)
        if form.is_valid():
            cleaning_request = form.save(commit=False)
            cleaning_request.cleaning_listing = cleaning_listing
            cleaning_request.save()
            return redirect('cleaning_listings_browse')
    data = {
        'listing_id': listing_id,
        'form': CleaningRequestForm(homeowner=homeowner)
    }
    return render(request, 'webapp/cleaning_listing_apply.html', data)

@login_required(login_url='login')
def cleaning_listing_delete(request, listing_id):
    listing = get_object_or_404(CleaningListing, id=listing_id) 
    listing.delete()
    return redirect('cleaning_listings_browse')

@login_required(login_url='login')
def cleaning_request_accept(request, request_id):
    cleaning_request = CleaningRequest.objects.get(id=request_id)
    if cleaning_request.cleaning_listing.cleaner.user != request.user:
        return redirect('dashboard')
    cleaning_request.status = CleaningRequestStatus.PENDING_CLEANING
    cleaning_request.save()
    return redirect('dashboard')

@login_required(login_url='login')
def cleaning_request_decline(request, request_id):
    cleaning_request = CleaningRequest.objects.get(id=request_id)
    if cleaning_request.cleaning_listing.cleaner.user != request.user:
        return redirect('dashboard')
    cleaning_request.status = CleaningRequestStatus.DECLINED
    cleaning_request.save()
    return redirect('dashboard')

@login_required(login_url='login')
def cleaning_request_review(request, request_id):
    cleaning_request = CleaningRequest.objects.get(id=request_id)
    if cleaning_request.property.homeowner.user != request.user:
        return redirect('dashboard')
    form = CleaningRequestReviewForm()
    if request.method == 'POST':
        form = CleaningRequestReviewForm(request.POST, instance=cleaning_request)
        if form.is_valid():
            cleaning_request.status = CleaningRequestStatus.COMPLETED
            cleaning_request.rating = form.cleaned_data['rating']
            cleaning_request.feedback = form.cleaned_data['feedback']
            cleaning_request.save()
            refresh_cleaner_rating(cleaning_request.cleaning_listing.cleaner)
            return redirect('dashboard')
    return render(request, 'webapp/cleaning_request_review.html', {
        'form': form,
        'cleaning_request': cleaning_request,
    })

def refresh_cleaner_rating(cleaner):
    all_requests = CleaningRequest.objects.filter(
        Q(cleaning_listing__cleaner=cleaner) & Q(status=CleaningRequestStatus.COMPLETED)
    )
    cleaner.rating = sum([request.rating for request in all_requests]) / len(all_requests)
    cleaner.save()

@login_required(login_url='login')
def cleaning_request_completed(request, request_id):
    cleaning_request = CleaningRequest.objects.get(id=request_id)
    if cleaning_request.cleaning_listing.cleaner.user != request.user:
        return redirect('dashboard')
    cleaning_request.status = CleaningRequestStatus.PENDING_REVIEW
    cleaning_request.save()
    return redirect('dashboard')

@login_required(login_url='login')
def service_category_create(request):
    if request.user.role != 'platform_manager':
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if ServiceCategory.objects.filter(name=name).exists():
                messages.error(request, 'Service category already exists.')
            else:
                form.save()
                messages.success(request, 'Service category added successfully.')
                return redirect('service_category_view')
            
    else:
        form = ServiceCategoryForm()
        
    return render(request, 'webapp/service_category_create.html', {'form': form})

@login_required(login_url='login')
def service_category_view(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'webapp/service_category_view.html', {'categories': categories})

@login_required(login_url='login')
def service_category_delete(request, category_id):
    category = get_object_or_404(ServiceCategory, id=category_id)
    category.delete()
    return redirect('service_category_view')

    
def logout(request):
    auth.logout(request)
    return redirect('login')
