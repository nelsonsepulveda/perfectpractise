from rest_framework import permissions
from billing.models import BillingInfo


class IsPaid(permissions.BasePermission):
    """
    Allows access only to paid users.
    """
    message = 'Free version has limited permission.'

    def has_permission(self, request, view):
        try:
            billing_info = BillingInfo.objects.get(user=request.user)
            return billing_info.is_active

        except BillingInfo.DoesNotExist:
            return False
