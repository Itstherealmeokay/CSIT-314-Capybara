from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name=''),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'), 
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('view_profile/', views.view_profile, name='view_profile'),
    path('cleaner/<int:pk>/', views.CleanerProfile.as_view(), name='cleaner_profile'),
    path('browsecleaners/', views.browse_cleaners, name='browsecleaners'),
    path('cleaning_listings/', views.cleaning_listings, name='cleaning_listings'),
    path('cleaner/listings/create/', views.create_cleaning_listing, name='create_cleaning_listing'),
]
