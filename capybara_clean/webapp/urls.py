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
    path('browsecleaninglistings/', views.browse_cleaning_listings, name='browse_cleaning_listings'),
    path('cleaner/listings/create/', views.create_cleaning_listing, name='create_cleaning_listing'),
    path('cleaner/listings/<int:listing_id>/delete/', views.delete_cleaning_listing, name='delete_cleaning_listing'),
    path('cleaner/listings/<int:listing_id>/', views.view_listing, name='view_listing'),

    path('service_category/create/', views.service_category_create, name='service_category_create'),
    path('service_category/', views.service_category_view, name='service_category_view'),
    path('service_category/<int:category_id>/delete/', views.service_category_delete, name='service_category_delete'),
]


