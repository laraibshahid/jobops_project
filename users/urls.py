from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management (Admin only)
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # User profile
    path('profile/', views.user_info_view, name='user-info'),
    path('profile/update/', views.UserProfileView.as_view(), name='user-profile'),
    path('change-password/', views.change_password_view, name='change-password'),
] 