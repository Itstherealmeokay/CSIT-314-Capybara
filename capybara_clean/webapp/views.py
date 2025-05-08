from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, Value, Avg
from django.db.models.functions import Concat
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from .forms import *
from .models import *

class HomeView(View):
    def get(self, request):
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
    
class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = UserProfileForm(instance=profile)
        return render(request, 'webapp/edit_profile.html', {'form': form})

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
        return render(request, 'webapp/edit_profile.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'webapp/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        user, error_message = CustomUser.authenticate_user(username, password)
        if user:
            auth.login(request, user)
            return redirect(user.get_dashboard_url())
        else:
            messages.error(request, error_message)
            return render(request, 'webapp/login.html', {'form': form})
class Dashboard(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        dashdata = ViewDashboard().get_dash(request)
        return render(request, 'webapp/dashboard.html', dashdata)

class ViewUserProfile(LoginRequiredMixin, View):
    def get(self, request):
        data = UserProfile().get_profile_info(request)
        return render(request, 'webapp/view_profile.html', data)

class BrowseCleaners(LoginRequiredMixin, View):
    def get(self, request, pk):
        data = Homeowner.get_homeowner(request).get_cleaner_profile_data(pk)
        return render(request, 'webapp/cleaner_profile.html', data)

    def post(self, request, pk):
        data = Homeowner.get_homeowner(request).update_cleaner_favourite(pk)
        return render(request, 'webapp/cleaner_profile.html', data)

class PropertyCreateView(LoginRequiredMixin, View):
    def get(self, request):
        webpage = Homeowner().is_homeowner(request)
        form = PropertyForm()
        return render(request, webpage, {'form': form})

    def post(self, request):
        redirect_response = Homeowner.create_property_from_post(request)
        return redirect_response  # always redirect after successful POST



class PropertyUpdateView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, property_id):
        return render(request, *Homeowner.get_property_update_form(request, property_id))

    def post(self, request, property_id):
        return render(request, *Homeowner.update_property_from_post(request, property_id))

    

class PropertyDeleteView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, property_id):
        Homeowner.delete_property_by_id(request, property_id)
        return redirect('view_profile')




class BrowseCleanersView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        return render(request, *Homeowner.get_cleaner_browser_data(request))

    def post(self, request):
        return render(request, *Homeowner.handle_cleaner_favourite_removal(request))

class CleaningListingsBrowse(LoginRequiredMixin, View):
    def get(self, request):
        data = CleaningListing.get_browse_context(request)
        if 'redirect' in data:
            return redirect(data['redirect'])
        return render(request, 'webapp/cleaning_listings_browse.html', data)


class CleaningListingDetailView(LoginRequiredMixin, View):
    def get(self, request, listing_id):
        listing = get_object_or_404(CleaningListing, id=listing_id)
        context = listing.get_detail_context_for_user(request.user)
        return render(request, 'webapp/cleaning_listing_view.html', context)

class CleaningListingCreate(LoginRequiredMixin, View):
    def get(self, request):
        context = CleaningListing.get_create_context(request)
        if 'redirect' in context:
            return redirect(context['redirect'])
        return render(request, 'webapp/cleaning_listing_create.html', context)

    def post(self, request):
        context = CleaningListing.create_from_request(request)
        if 'redirect' in context:
            return redirect(context['redirect'])
        return render(request, 'webapp/cleaning_listing_create.html', context)


class HomeViewListings(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        context = CleaningListing.get_home_view_listing_context(pk)
        return render(request, 'webapp/homeviewlisting.html', context)


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
def cleaning_listing_favourite(request, listing_id):
    if request.user.role != 'homeowner':
        return redirect('cleaning_listings_view', listing_id)
    listing = get_object_or_404(CleaningListing, id=listing_id)
    homeowner = Homeowner.objects.get(user=request.user)
    if request.method == 'POST':
        if 'add_favourite' in request.POST:
            homeowner.favourite_listings.add(listing)
        else:
            homeowner.favourite_listings.remove(listing)
        if request.POST.get('redirect'):
            return redirect(request.POST.get('redirect'))
    return redirect('cleaning_listings_browse')

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


class SearchRequestHistory(LoginRequiredMixin, View):
    def get(self, request):
        all_requests, search_query = CleaningRequest.get_filtered_requests(request)

        return render(request, 'webapp/request_history.html', {
            'all_requests': all_requests,
            'search_query': search_query   
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
