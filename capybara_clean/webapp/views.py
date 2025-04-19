from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, UserProfileForm
from . models import UserProfile
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'webapp/index.html')

def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    context = {'form': form}
    return render(request, 'webapp/register.html', context)

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
def login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm()
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')

    context = {'form': form}
    return render(request, 'webapp/login.html', context)


@login_required(login_url='login')
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        return render(request, 'webapp/admin_dashboard.html', {'user': user})
    elif user.role == 'homeowner':
        return render(request, 'webapp/homeowner_dashboard.html', {'user': user})
    elif user.role == 'cleaner':
        return render(request, 'webapp/cleaner_dashboard.html', {'user': user})

def view_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'webapp/view_profile.html', {'profile': profile})

def logout(request):
    auth.logout(request)
    return redirect('login')
