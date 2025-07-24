from django.urls import path
from accounts.views import Dashboard, Login, Register, Logout

app_name = 'accounts'

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),
    
]
