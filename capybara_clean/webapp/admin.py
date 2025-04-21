from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

admin.site.register(CustomUser, UserAdmin)

from .models import Homeowner, Cleaner, Property, CleaningRequest
admin.site.register([Homeowner, Cleaner, Property, CleaningRequest])