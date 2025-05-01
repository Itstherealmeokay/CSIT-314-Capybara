from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name=''),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'), 

    path('dashboard/', views.dashboard, name='dashboard'),

    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('view_profile/', views.view_profile, name='view_profile'),

    path('browsecleaners/', views.browse_cleaners, name='browsecleaners'),
    path('cleaner/<int:pk>/', views.CleanerProfile.as_view(), name='cleaner_profile'),
    path('cleaning_listings/', views.cleaning_listings, name='cleaning_listings'),
    path('cleaner/listings/create/', views.create_cleaning_listing, name='create_cleaning_listing'),
    path('cleaner/listings/<int:listing_id>/delete/', views.delete_cleaning_listing, name='delete_cleaning_listing'),
    path('cleaner/listings/<int:listing_id>/', views.view_listing, name='view_listing'),

    path('add_service_category/', views.add_service_category, name='add_service_category'),
    path('view_category/', views.view_service_category, name='view_category'),
    path('delete_service_category/<int:category_id>/', views.delete_service_category, name='delete_service_category'),
]


