from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from billing.models import BillingInfo, StripeInfo


class PaywallMixin(object):
    billing_info = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            self.billing_info = BillingInfo.objects.get(user=self.request.user)

        except BillingInfo.DoesNotExist:
            self.billing_info = None

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sub_fee'] = StripeInfo.get_subscription_price()
        context['billing_info'] = self.billing_info

        if self.billing_info is None:
            context['has_active_payment'] = None
        else:
            context['has_active_payment'] = self.billing_info.is_active

        return context
