from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name=''),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'), 

    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),

    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('view_profile/', views.ViewUserProfile.as_view(), name='view_profile'),

    path('browsecleaners/', views.BrowseCleanersView.as_view(), name='browsecleaners'),
    path('cleaner/<int:pk>/', views.BrowseCleaners.as_view(), name='cleaner_profile'),
    path('browsecleaninglistings/', views.CleaningListingsBrowse.as_view(), name='cleaning_listings_browse'),
    path('cleaner/listings/create/', views.CleaningListingCreate.as_view(), name='cleaning_listing_create'),
    path('cleaner/listings/<int:listing_id>/', views.CleaningListingDetailView.as_view(), name='cleaning_listing_view'),
    path('cleaner/listings/<int:listing_id>/update', views.CleaningListingUpdate.as_view(), name='cleaning_listing_update'),
    path('cleaner/listings/<int:listing_id>/delete/', views.CleaningListingDelete.as_view(), name='cleaning_listing_delete'),
    path('cleaner/listings/<int:listing_id>/apply/', views.ApplyCleaningListing.as_view(), name='cleaning_listing_apply'),
    path('cleaner/listings/<int:listing_id>/favourite/', views.CleaningListingFavourite.as_view(), name='cleaning_listing_favourite'),
    path('cleaner/<int:pk>/listings/', views.HomeViewListings.as_view(), name='cleaner_listings_view'),
    path('request_history/', views.SearchRequestHistory.as_view(), name='request_history'),

    path('cleaner/requests/<int:request_id>/accept/', views.cleaning_request_accept, name='cleaning_request_accept'),
    path('cleaner/requests/<int:request_id>/decline/', views.cleaning_request_decline, name='cleaning_request_decline'),
    path('cleaner/requests/<int:request_id>/completed/', views.cleaning_request_completed, name='cleaning_request_completed'),
    path('cleaner/requests/<int:request_id>/review/', views.cleaning_request_review, name='cleaning_request_review'),

    path('property/create/', views.PropertyCreateView.as_view(), name='property_create'),
    path('property/<int:property_id>/update', views.PropertyUpdateView.as_view(), name='property_update'),
    path('property/<int:property_id>/delete', views.PropertyDeleteView.as_view(), name='property_delete'),

    path('service_category/create/', views.service_category_create, name='service_category_create'),
    path('service_category/', views.service_category_view, name='service_category_view'),
    path('service_category/<int:category_id>/delete/', views.service_category_delete, name='service_category_delete'),
]


