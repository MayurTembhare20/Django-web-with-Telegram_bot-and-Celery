from django.urls import include, path
from rest_framework.routers import DefaultRouter
from myapp import views

router = DefaultRouter()

# router.register('api',views.DataViewsetAPI)
# router.register('dataapi',views.DataModelViewsetAPI)

from django.urls import path
from myapp.views import SendPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserPasswordResetView
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
 
#  for selery email
    path('sendmail/', views.send_mail_to_all, name="sendmail"),
    path('schedulemail/', views.schedule_mail, name="schedulemail"),

# for router
    path('',include(router.urls)),
    path('',include('rest_framework.urls')),
]