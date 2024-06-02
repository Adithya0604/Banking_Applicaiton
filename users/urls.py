from django.urls import path
from .views import UserApiView, InsertingUserDataApiView , PatchApiView


urlpatterns = [
    path('', UserApiView.as_view(), name='user-list'),
    path('create-user', InsertingUserDataApiView.as_view(), name='user-add'),
    path('update-user/<int:userID>', PatchApiView.as_view(), name='update')
]