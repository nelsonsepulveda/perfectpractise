from django.urls import path
from django.contrib.auth import views as auth_views

from .forms import LoginForm
from .views import ProfileUpdateView

urlpatterns = [

    path('login/', auth_views.login, {'template_name': 'profiles/signin.html', 'authentication_form': LoginForm}, name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),
    path('profile/<int:pk>/', ProfileUpdateView.as_view(), name='profile'),

    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
