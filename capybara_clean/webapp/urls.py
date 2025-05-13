from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeViewController.as_view(), name=''),
    path('register/', views.RegisterViewController.as_view(), name='register'),
    path('login/', views.LoginViewController.as_view(), name='login'),
    path('logout/', views.logout, name='logout'), 

    path('dashboard/', views.DashboardController.as_view(), name='dashboard'),

    path('edit_profile/', views.EditProfileViewController.as_view(), name='edit_profile'),
    path('view_profile/', views.ViewUserProfileController.as_view(), name='view_profile'),
    path('adminuserupdate/<int:user_id>/', views.AdminUserEditController.as_view(), name='adminuserupdate'),
    path('adminuser/<int:user_id>/edit-account/', views.AdminUserAccountEditController.as_view(), name='adminuser_edit_account'),
    path('adminuser/suspend/<int:user_id>/', views.AdminUserSuspendToggleController.as_view(), name='adminuser_suspend_toggle'),

    
    path('browsecleaners/', views.BrowseCleanersViewController.as_view(), name='browsecleaners'),
    path('cleaner/<int:pk>/', views.BrowseCleanersController.as_view(), name='cleaner_profile'),
    path('browsecleaninglistings/', views.CleaningListingsBrowseController.as_view(), name='cleaning_listings_browse'),
    path('cleaner/listings/create/', views.CleaningListingCreateController.as_view(), name='cleaning_listing_create'),
    path('cleaner/listings/<int:listing_id>/', views.CleaningListingDetailController.as_view(), name='cleaning_listing_view'),
    path('cleaner/listings/<int:listing_id>/update', views.CleaningListingUpdateController.as_view(), name='cleaning_listing_update'),
    path('cleaner/listings/<int:listing_id>/delete/', views.CleaningListingDeleteController.as_view(), name='cleaning_listing_delete'),
    path('cleaner/listings/<int:listing_id>/apply/', views.ApplyCleaningListingController.as_view(), name='cleaning_listing_apply'),
    path('cleaner/listings/<int:listing_id>/favourite/', views.CleaningListingFavouriteController.as_view(), name='cleaning_listing_favourite'),
    path('cleaner/<int:pk>/listings/', views.HomeViewListingsController.as_view(), name='cleaner_listings_view'),
    path('request_history/', views.SearchRequestHistoryController.as_view(), name='request_history'),

    path('cleaner/requests/<int:request_id>/accept/', views.cleaning_request_accept, name='cleaning_request_accept'),
    path('cleaner/requests/<int:request_id>/decline/', views.cleaning_request_decline, name='cleaning_request_decline'),
    path('cleaner/requests/<int:request_id>/completed/', views.cleaning_request_completed, name='cleaning_request_completed'),
    path('cleaner/requests/<int:request_id>/review/', views.cleaning_request_review, name='cleaning_request_review'),

    path('property/create/', views.PropertyCreateController.as_view(), name='property_create'),
    path('property/<int:property_id>/update', views.PropertyUpdateController.as_view(), name='property_update'),
    path('property/<int:property_id>/delete', views.PropertyDeleteController.as_view(), name='property_delete'),

    path('service_category/create/', views.ServiceCategoryCreateController.as_view(), name='service_category_create'),
    path('service_category/', views.ServiceCategoryListController.as_view(), name='service_category_view'),
    path('service_category/<int:category_id>/update/', views.ServiceCategoryUpdateController.as_view(), name='service_category_update'),
    path('service_category/<int:category_id>/delete/', views.ServiceCategoryDeleteController.as_view(), name='service_category_delete'),
]


