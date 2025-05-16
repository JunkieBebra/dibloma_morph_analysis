from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TextViewSet, WordDetailAPIView, DictionaryViewSet, DictionaryEntryViewSet
from .views_auth import RegisterView, LoginView, LogoutView

router = DefaultRouter()
router.register(r'texts', TextViewSet, basename='text')
router.register(r'dictionaries', DictionaryViewSet, basename='dictionary')
router.register(r'dictionaries-entry', DictionaryEntryViewSet, basename='dictionary-entry')


urlpatterns = [
    path('', include(router.urls)),
    path("words/<int:pk>/", WordDetailAPIView.as_view(), name="word-detail"),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]