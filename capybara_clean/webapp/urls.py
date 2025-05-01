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
    path('browsecleaninglistings/', views.cleaning_listings_browse, name='cleaning_listings_browse'),
    path('cleaner/listings/create/', views.cleaning_listing_create, name='cleaning_listing_create'),
    path('cleaner/listings/<int:listing_id>/', views.cleaning_listing_view, name='cleaning_listing_view'),
    path('cleaner/listings/<int:listing_id>/update', views.cleaning_listing_update, name='cleaning_listing_update'),
    path('cleaner/listings/<int:listing_id>/delete/', views.cleaning_listing_delete, name='cleaning_listing_delete'),
    path('cleaner/listings/<int:listing_id>/apply/', views.cleaning_listing_apply, name='cleaning_listing_apply'),

    path('property/create/', views.property_create, name='property_create'),
    path('property/<int:property_id>/update', views.property_update, name='property_update'),
    path('property/<int:property_id>/delete', views.property_delete, name='property_delete'),

    path('service_category/create/', views.service_category_create, name='service_category_create'),
    path('service_category/', views.service_category_view, name='service_category_view'),
    path('service_category/<int:category_id>/delete/', views.service_category_delete, name='service_category_delete'),
]


