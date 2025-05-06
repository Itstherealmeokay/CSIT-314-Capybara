from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *



@admin.action(description="Suspend selected users")
def suspend_users(modeladmin, request, queryset):
    queryset.update(is_suspended=True)
    

@admin.action(description="Unsuspend selected users")
def unsuspend_users(modeladmin, request, queryset):
    queryset.update(is_suspended=False)
    
    
class CustomUserAdmin(UserAdmin):
    # Add the `role` field to both the edit and create forms in the admin
    fieldsets = UserAdmin.fieldsets + (
        ("Role Info", {"fields": ("role", "is_suspended")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role Info", {"fields": ("role", "is_suspended")}),
    )
    
    actions = [suspend_users, unsuspend_users]

    # Optional: Show role in the list view
    list_display = ["username", "email", "first_name", "last_name", "role", "is_staff", "is_suspended"]
    list_filter = ["role", "is_staff", "is_suspended"]

# Register with the custom admin
admin.site.register(CustomUser, CustomUserAdmin)


# Register other models as usual
admin.site.register([
    UserProfile,
    Homeowner,
    Cleaner,
    PlatformManager,
    Property,
    CleaningRequest,
    ServiceCategory,
    CleaningListing,
    CleaningListingView,
])
