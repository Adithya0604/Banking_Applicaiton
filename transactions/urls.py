from django.urls import path
from .views import PostApiView , PatchApiView



urlpatterns = [
    path('Money/', PostApiView.as_view(), name='Money-Money'),
    path('Update_Status/' , PatchApiView.as_view() , name = 'Update-Update')
]
