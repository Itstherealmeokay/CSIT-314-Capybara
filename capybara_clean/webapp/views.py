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

class HomeViewController(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'webapp/index.html')

class RegisterViewController(View):
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
        elif role == 'adminuser':
            AdminUser.objects.create(user=user)
        return redirect('login')
    
class EditProfileViewController(LoginRequiredMixin, View):
    def get(self, request):
        context = UserProfile.get_edit_context(request)
        return render(request, 'webapp/edit_profile.html', context)

    def post(self, request):
        success, context = UserProfile.handle_edit_submission(request)
        if success:
            return redirect('view_profile')
        return render(request, 'webapp/edit_profile.html', context)


class AdminUserEditController(LoginRequiredMixin, View):
    def get(self, request, user_id):
        context = UserProfile.get_admin_edit_context(user_id)
        return render(request, 'webapp/adminuserupdate.html', context)

    def post(self, request, user_id):
        success, context = UserProfile.handle_admin_edit_submission(request, user_id)
        if success:
            return redirect('dashboard')  # Or wherever your admin dashboard is
        return render(request, 'webapp/adminuserupdate.html', context)
    

class AdminUserAccountEditController(LoginRequiredMixin, View):
    def get(self, request, user_id):
        form, user_obj = AdminUser.get_user_account_form(user_id)
        return render(request, 'webapp/adminuser_edit_account.html', {'form': form, 'user_obj': user_obj})

    def post(self, request, user_id):
        success, result = AdminUser.save_user_account_form(request, user_id)
        if success:
            return redirect('dashboard')
        return render(request, 'webapp/adminuser_edit_account.html', {'form': result, 'user_obj': CustomUser.objects.get(id=user_id)})


class AdminUserSuspendToggleController(LoginRequiredMixin, View):
    def post(self, request, user_id):
        AdminUser.toggle_suspension(user_id)
        return redirect('dashboard')  # Or wherever your dashboard is


class LoginViewController(View):
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
class DashboardController(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        dashdata = ViewDashboard().get_dash(request)
        return render(request, 'webapp/dashboard.html', dashdata)

class ViewUserProfileController(LoginRequiredMixin, View):
    def get(self, request):
        data = UserProfile().get_profile_info(request)
        return render(request, 'webapp/view_profile.html', data)

class BrowseCleanersController(LoginRequiredMixin, View):
    def get(self, request, pk):
        data = Homeowner.get_homeowner(request).get_cleaner_profile_data(pk)
        return render(request, 'webapp/cleaner_profile.html', data)

    def post(self, request, pk):
        data = Homeowner.get_homeowner(request).update_cleaner_favourite(pk)
        return render(request, 'webapp/cleaner_profile.html', data)

class PropertyCreateController(LoginRequiredMixin, View):
    def get(self, request):
        webpage = Homeowner().is_homeowner(request)
        form = PropertyForm()
        return render(request, webpage, {'form': form})

    def post(self, request):
        redirect_response = Homeowner.create_property_from_post(request)
        return redirect_response  # always redirect after successful POST


class PropertyUpdateController(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, property_id):
        return render(request, *Homeowner.get_property_update_form(request, property_id))

    def post(self, request, property_id):
        return render(request, *Homeowner.update_property_from_post(request, property_id))

    

class PropertyDeleteController(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, property_id):
        Homeowner.delete_property_by_id(request, property_id)
        return redirect('view_profile')




class BrowseCleanersViewController(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        return render(request, *Homeowner.get_cleaner_browser_data(request))

    def post(self, request):
        return render(request, *Homeowner.handle_cleaner_favourite_removal(request))

class CleaningListingsBrowseController(LoginRequiredMixin, View):
    def get(self, request):
        data = CleaningListing.get_browse_context(request)
        if 'redirect' in data:
            return redirect(data['redirect'])
        return render(request, 'webapp/cleaning_listings_browse.html', data)


class CleaningListingDetailController(LoginRequiredMixin, View):
    def get(self, request, listing_id):
        listing = get_object_or_404(CleaningListing, id=listing_id)
        context = listing.get_detail_context_for_user(request.user)
        return render(request, 'webapp/cleaning_listing_view.html', context)

class CleaningListingCreateController(LoginRequiredMixin, View):
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


class HomeViewListingsController(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        context = CleaningListing.get_home_view_listing_context(pk)
        return render(request, 'webapp/homeviewlisting.html', context)


class CleaningListingUpdateController(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, listing_id):
        context = CleaningListing.get_update_context(request, listing_id)
        return render(request, 'webapp/cleaning_listing_update.html', context)

    def post(self, request, listing_id):
        context = CleaningListing.post_update_context(request, listing_id)
        if 'redirect' in context:
            return redirect(context['redirect'])
        return render(request, 'webapp/cleaning_listing_update.html', context)


class CleaningListingFavouriteController(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, listing_id):
        context = CleaningListing.handle_favourite_action(request, listing_id)
        return redirect(context['redirect'])


class ApplyCleaningListingController(LoginRequiredMixin, View):
    login_url = 'login'
    
    def get(self, request, listing_id):
        context = CleaningListing.get_application_context(request, listing_id)
        if 'redirect' in context:
            return redirect(context['redirect'])
        return render(request, 'webapp/cleaning_listing_apply.html', context)

    def post(self, request, listing_id):
        context = CleaningListing.process_application_post(request, listing_id)
        if 'redirect' in context:
            return redirect(context['redirect'])
        return render(request, 'webapp/cleaning_listing_apply.html', context)
    
class CleaningListingDeleteController(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, listing_id):
        redirect_to = CleaningListing.handle_delete(request, listing_id)
        return redirect(redirect_to)

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


class SearchRequestHistoryController(LoginRequiredMixin, View):
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

class ServiceCategoryCreateController(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        context = ServiceCategory.get_create_context(request)
        return render(request, 'webapp/service_category_create.html', context)

    def post(self, request):
        context = ServiceCategory.handle_create_submission(request)
        if context.get('redirect'):
            return redirect(context['redirect'])
        return render(request, 'webapp/service_category_create.html', context)


class ServiceCategoryListController(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request):
        context = ServiceCategory.get_list_context()
        return render(request, 'webapp/service_category_view.html', context)


class ServiceCategoryDeleteController(LoginRequiredMixin, View):
    login_url = 'login'
    def post(self, request, category_id):
        context = ServiceCategory.handle_delete(request, category_id)
        return redirect(context.get('redirect', 'service_category_view'))


    
def logout(request):
    auth.logout(request)
    return redirect('login')
