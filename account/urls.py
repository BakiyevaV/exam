from django.contrib.auth import logout
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from account.views import RegisterApi, ConfirmApi, activated, GetUserData, DownloadPDFView, AuthenticateUserView,\
	login_view, logout_view, get_private, SaveUserInfoApi

app_name = 'user'

urlpatterns = [
	path('api/register/', RegisterApi.as_view(), name='register'),
	path('api/confirm/<int:pk>/', ConfirmApi.as_view(), name='confirm'),
	path('api/getUserData/', GetUserData.as_view(), name='get_user_data'),
	path('activated/<int:pk>/', activated, name='activated'),
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
	path('api/download-pdf/', DownloadPDFView.as_view(), name='download-pdf'),
	path('api/authenticate/', AuthenticateUserView.as_view(), name='authenticate'),
	path('login/', login_view, name='login'),
	path('logout/', logout_view, name='logout'),
	path('private/<int:pk>/', get_private, name='private'),
	path('api/save/<int:pk>/', SaveUserInfoApi.as_view(), name='save'),

]