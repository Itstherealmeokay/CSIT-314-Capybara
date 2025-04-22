from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Homeowner, Cleaner, Property, CleaningRequest

class CustomUserAdmin(UserAdmin):
    # Add the `role` field to both the edit and create forms in the admin
    fieldsets = UserAdmin.fieldsets + (
        ("Role Info", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role Info", {"fields": ("role",)}),
    )

    # Optional: Show role in the list view
    list_display = ["username", "email", "first_name", "last_name", "role", "is_staff"]
    list_filter = ["role", "is_staff"]

# Register with the custom admin
admin.site.register(CustomUser, CustomUserAdmin)

# Register other models as usual
admin.site.register([Homeowner, Cleaner, Property, CleaningRequest])
