from django.urls import path
from . import views
urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Pages
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    

    # Laundry
    path('request/', views.request_view, name='laundry_request'),

    # Tracking
    path('track/', views.track_view, name='track'),
    path('track/details/', views.tracking_details_view, name='tracking_details'),

    # Order History
    path('my-orders/', views.my_orders_view, name='my_orders'),

    # Admin
    path('adminlogin/', views.admin_login_view, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('update-status/<int:order_id>/', views.update_status_view, name='update_status'),
    path('delete-order/<int:order_id>/', views.delete_order_view, name='delete_order'),
]
