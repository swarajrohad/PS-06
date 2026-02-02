from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.user_login, name='login'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/mechanic/', views.register_mechanic, name='register_mechanic'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    path('user/home/', views.user_home, name='user_home'),
    path('request/create/', views.create_request, name='create_request'),
    path('request/<int:request_id>/status/', views.request_status, name='request_status'),
    
    path('mechanic/dashboard/', views.mechanic_dashboard, name='mechanic_dashboard'),
    path('mechanic/request/<int:request_id>/<str:action>/', views.mechanic_update_request, name='mechanic_update_request'),
    path('mechanic/update_location/', views.update_location, name='update_location'),
    path('mechanic/toggle_availability/', views.toggle_availability, name='toggle_availability'),
]
