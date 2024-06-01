from django.urls import path
from .views import UserApiView, InsertingUserDataApiView


urlpatterns = [
    path('', UserApiView.as_view(), name='user-list'),
    path('create-user', InsertingUserDataApiView.as_view(), name='user-add'),
    # path('users/', InsertingUserDataApiView.as_view(), name='user-create')
]