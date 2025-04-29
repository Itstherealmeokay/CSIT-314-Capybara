from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect


from .forms import CreateUserForm, LoginForm, UserProfileForm, CleaningListingForm, ServiceCategoryForm
from .models import UserProfile, Homeowner, Cleaner, CleaningListing, PlatformManager, ServiceCategory  


def home(request):
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
            return redirect('dashboard')
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


@login_required(login_url='login')
def dashboard(request):
    user = request.user
    if user.is_staff:
        return redirect('/admin/')
    elif user.role == 'homeowner':
        return render(request, 'webapp/dashboard_homeowner.html', {'user': user})
    elif user.role == 'cleaner':
        return render(request, 'webapp/dashboard_cleaner.html', {'user': user})
    elif user.role == 'platform_manager':
        return render(request, 'webapp/dashboard_platformmanager.html', {'user': user})
    return HttpResponse(f"Unknown role {user}")

@login_required(login_url='login')
def view_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'webapp/view_profile.html', {'profile': profile})

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
def browse_cleaners(request):
    query = request.GET.get('q')
    cleaners = Cleaner.objects.all()
    favourite_cleaners = Homeowner.objects.get(user=request.user).favourite_cleaners.all()

    if query:
        cleaners = Cleaner.objects.filter(user__username__icontains=query)

    return render(request, 'webapp/browsecleaners.html', {'cleaners': cleaners, 'query': query, 'favourite_cleaners': favourite_cleaners})

@login_required(login_url='login')
def cleaning_listings(request):
    if request.user.role != 'cleaner':
        return redirect('dashboard')  # prevent unauthorized access

    listings = CleaningListing.objects.all()
    return render(request, 'webapp/cleaning_listings.html', {'listings': listings})

@login_required
def create_cleaning_listing(request):
    if request.user.role != 'cleaner':
        return redirect('dashboard')

    if request.method == 'POST':
        form = CleaningListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.status = 'active'  # or set default
            listing.save()
            return redirect('cleaning_listings')
    else:
        form = CleaningListingForm()

    return render(request, 'webapp/create_cleaning_listing.html', {'form': form})

@login_required(login_url='login')
def delete_cleaning_listing(request, listing_id):
    listing = get_object_or_404(CleaningListing, id=listing_id) 
    listing.delete()
    return redirect('cleaning_listings')

@login_required(login_url='login')
def add_service_category(request):
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
                return redirect('dashboard')
            
    else:
        form = ServiceCategoryForm()
        
    return render(request, 'webapp/add_category.html', {'form': form})

def view_service_category(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'webapp/view_category.html', {'categories': categories})

def logout(request):
    auth.logout(request)
    return redirect('login')
