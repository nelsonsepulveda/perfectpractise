import datetime
import pytz

from django.conf import settings
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from core.mixins import PaywallMixin
from billing.forms import BillingForm
from billing.models import StripeInfo

import stripe

stripe.api_key = settings.STRIPE_PRIVATE_KEY
stripe.api_version = '2018-10-31'


class BillingInfo(PaywallMixin, CreateView):
    template_name = 'billing/billing_info.html'
    form_class = BillingForm

    def get_success_url(self):
        return reverse_lazy('billing_info', kwargs={'pk': self.request.user.id})

    def get_initial(self):
        return {
            'email': self.request.user.email,
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['stripe_api_key'] = settings.STRIPE_PUBLIC_KEY

        # get customer info from stripe
        if self.billing_info and self.billing_info.brand is None:
            try:
                customer_resp = stripe.Customer.retrieve(self.billing_info.customer_id)

                self.billing_info.email = customer_resp.email
                self.billing_info.last4 = customer_resp.sources.data[0]['last4']
                self.billing_info.brand = customer_resp.sources.data[0]['brand']
                self.billing_info.exp_month = customer_resp.sources.data[0]['exp_month']
                self.billing_info.exp_year = customer_resp.sources.data[0]['exp_year']
                self.billing_info.city = customer_resp.sources.data[0]['address_city']
                self.billing_info.state = customer_resp.sources.data[0]['address_state']
                self.billing_info.country = customer_resp.sources.data[0]['address_country']
                self.billing_info.address_line1 = customer_resp.sources.data[0]['address_line1']
                self.billing_info.address_line2 = customer_resp.sources.data[0]['address_line2']
                self.billing_info.post_code = customer_resp.sources.data[0]['address_zip']
                self.billing_info.save()

                context['billing_info'] = self.billing_info
            except Exception:
                pass

        return context

    def form_valid(self, form):

        billing_obj = form.save(commit=False)

        try:
            plan_id = StripeInfo.get_plan_id()
            stripe_token = form.cleaned_data.get('stripe_token')
            email = form.cleaned_data.get('email')

            # create customer
            cus_resp = stripe.Customer.create(
                source=stripe_token,
                email=email
            )

            billing_obj.customer_id = cus_resp['id']

            subs_resp = stripe.Subscription.create(
                customer=billing_obj.customer_id,
                items=[
                    {
                        "plan": plan_id,
                    },
                ]
            )

            billing_obj.subscription_id = subs_resp['id']
            billing_obj.subscription_status = subs_resp['status']
            billing_obj.created = datetime.datetime.fromtimestamp(subs_resp['created'], tz=pytz.UTC)
            billing_obj.current_period_start = datetime.datetime.fromtimestamp(subs_resp['current_period_start'],
                                                                               tz=pytz.UTC)
            billing_obj.current_period_end = datetime.datetime.fromtimestamp(subs_resp['current_period_end'],
                                                                             tz=pytz.UTC)

            billing_obj.user = self.request.user
            billing_obj.save()

        except Exception as e:
            messages.error(self.request, str(e))

        return redirect(self.get_success_url())
