from django.urls import path
from .views import PostApiView


urlpatterns = [
    path('Money/', PostApiView.as_view(), name='Money-Money'),
]
