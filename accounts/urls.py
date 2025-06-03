from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView, user_profile_view

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),    
    path('login/', UserLoginView.as_view(), name='login'),    
    path('logout/', UserLogoutView, name='logout'),    
    path('profile/', user_profile_view, name='profile'),
]
