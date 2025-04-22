from django.shortcuts import render, redirect
from django.views import View
from .forms import CreateUserForm, LoginForm, UserProfileForm
from . models import UserProfile, Homeowner, Cleaner
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


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
    return HttpResponse(f"Unknown role {user}")

def view_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'webapp/view_profile.html', {'profile': profile})

def browse_cleaners(request):
    return render(request, 'webapp/browsecleaners.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
