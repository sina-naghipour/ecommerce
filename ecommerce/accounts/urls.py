from django.urls import path
from accounts.views import (
    Dashboard, 
    Login, 
    Register, 
    Logout,
    UserListView,
    UserDetailView,
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
    UserToggleStatusView,
    UserAddAddressView,
    UserEditAddressView,
    UserDeleteAddressView,
    UserSetDefaultAddressView,
)

app_name = 'accounts'

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/toggle-status/', UserToggleStatusView.as_view(), name='user_toggle_status'),
    path('users/<int:user_id>/add-address/', UserAddAddressView.as_view(), name='user_add_address'),
    path('address/<int:pk>/edit/', UserEditAddressView.as_view(), name='user_edit_address'),
    path('address/<int:pk>/delete/', UserDeleteAddressView.as_view(), name='user_delete_address'),
    path('address/<int:pk>/set-default/', UserSetDefaultAddressView.as_view(), name='user_set_default_address'),
]
