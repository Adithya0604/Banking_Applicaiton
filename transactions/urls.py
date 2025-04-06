# ---------------------------- OLD URLS ------------------------------------

# from django.urls import path
# from .views import PostApiView , PatchApiView , GetApiView , GETApiView



# urlpatterns = [
#     path('Money/', PostApiView.as_view(), name='Money-Money'),
#     path('Update_Status/' , PatchApiView.as_view() , name = 'Update-Update'),
#     path('GET_Status/' , GetApiView.as_view() , name = 'GET-Details-of-transaction'),
#     path('GET_Status_1/' , GETApiView.as_view() , name = 'GET-Details-of-transaction_1')

# ]

# ---------------------------- New URLS ------------------------------------
from django.urls import path
from .views import PostApiView, PatchApiView, GetApiView, GetAllTransactionsApiView  # ✅ Fixed import

urlpatterns = [
    path('money/', PostApiView.as_view(), name='money-transaction'),  # ✅ Meaningful names
    path('update-status/', PatchApiView.as_view(), name='update-transaction-status'),
    path('get-status/', GetApiView.as_view(), name='get-transaction-details'),
    path('get-all-transactions/', GetAllTransactionsApiView.as_view(), name='get-all-transactions')  # ✅ Fixed the extra view
]
