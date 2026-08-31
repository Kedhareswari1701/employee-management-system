from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import AuthViewSet, UserViewSet

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
