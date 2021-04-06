from django.urls import path

from .views import BillingInfo


urlpatterns = [
    path('billing_info/<int:pk>/', BillingInfo.as_view(), name='billing_info'),
]
