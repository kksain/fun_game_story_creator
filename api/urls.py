from django.urls import path
from .views import (
    RegisterView,
    UserInfoView,
    StoryListCreateView,
    StoryDetailView,
    ContributionCreateView,
    ExportStoryView,
    LogoutView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', UserInfoView.as_view(), name='user-info'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('stories/', StoryListCreateView.as_view(), name='story-list'),
    path('stories/<int:pk>/', StoryDetailView.as_view(), name='story-detail'),
    path('stories/<int:pk>/contribute/',
         ContributionCreateView.as_view(), name='story-contribute'),
    path('stories/<int:pk>/export/',
         ExportStoryView.as_view(), name='story-export'),
]
