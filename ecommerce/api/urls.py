from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import *


app_name = 'api'

router = DefaultRouter()
router.register(r'login', LoginViewSet, basename='login')
router.register(r'logout', LogoutViewSet, basename='logout')
router.register(r'register', RegisterViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls))
]