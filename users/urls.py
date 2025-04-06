# ---------------------------- OLD URLS ------------------------------------
# from django.urls import path
# from .views import UserApiView, InsertingUserDataApiView , PatchApiView


# urlpatterns = [
#     path('', UserApiView.as_view(), name='user-list'),
#     path('create-user', InsertingUserDataApiView.as_view(), name='user-add'),
#     path('update-user/<int:userID>', PatchApiView.as_view(), name='update')
# ]

# ---------------------------- New URLS ------------------------------------
from django.urls import path
from .views import UserApiView, InsertingUserDataApiView, PatchApiView

urlpatterns = [
    path('', UserApiView.as_view(), name='user-list'),
    path('create-user/', InsertingUserDataApiView.as_view(), name='create-user'),  # ✅ Consistent naming
    path('update-user/<int:userID>/', PatchApiView.as_view(), name='update-user')  # ✅ Added trailing slash for consistency
]

# # ❌ Current
# path('users/', UserApiView.as_view(), name='user-list'),

# # ✅ FIXED
# path('', UserApiView.as_view(), name='user-list'),

