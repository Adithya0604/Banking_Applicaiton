from django.urls import path
from .views import PostApiView , PatchApiView , GetApiView



urlpatterns = [
    path('Money/', PostApiView.as_view(), name='Money-Money'),
    path('Update_Status/' , PatchApiView.as_view() , name = 'Update-Update'),
    path('GET_Status/' , GetApiView.as_view() , name = 'GET-Details-of-transaction')

]
