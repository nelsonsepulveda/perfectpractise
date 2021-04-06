from django.db import models
from django.conf import settings

from datetime import datetime
import stripe
import pytz

stripe.api_key = settings.STRIPE_PRIVATE_KEY
stripe.api_version = '2018-02-28'


class BillingInfo(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billing_info')

    customer_id = models.CharField(max_length=256, null=True, blank=True)
    subscription_id = models.CharField(max_length=256, null=True, blank=True)
    subscription_status = models.CharField(max_length=64, null=True, blank=True)  # trialing, active, past_due, canceled, unpaid

    last4 = models.CharField(max_length=4, null=True, blank=True)
    brand = models.CharField(max_length=50, null=True, blank=True)
    exp_month = models.IntegerField(null=True, blank=True)
    exp_year = models.IntegerField(null=True, blank=True)

    created = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    # billing details
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    address_line1 = models.CharField(max_length=256, null=True, blank=True)
    address_line2 = models.CharField(max_length=256, null=True, blank=True)
    postcode = models.CharField(max_length=128, null=True, blank=True)
    state = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def billing_name(self):
        if self.first_name and self.last_name:
            return ' '.join([self.first_name, self.last_name])
        else:
            return ''

    @property
    def is_active(self):
        if not self.is_in_curperiod():

            self.get_update_from_stripe()

        if self.subscription_status == "active":
            return True
        return False

    @property
    def is_subscribed(self):
        if self.subscription_id is not None:
            return True
        return False

    def is_in_curperiod(self):

        utc_now = datetime.now(tz=pytz.UTC)
        if self.current_period_end and utc_now < self.current_period_end:
            return True
        else:
            return False

    def get_update_from_stripe(self):
        if self.subscription_id is None:
            return None
        try:
            subs_resp = stripe.Subscription.retrieve(self.subscription_id)

            self.subscription_status = subs_resp['status']
            self.created = datetime.fromtimestamp(subs_resp['created'], tz=pytz.UTC)
            self.current_period_start = datetime.fromtimestamp(subs_resp['current_period_start'], tz=pytz.UTC)
            self.current_period_end = datetime.fromtimestamp(subs_resp['current_period_end'], tz=pytz.UTC)

            self.save()

        except Exception as retrieve_subs_exception:
            print(retrieve_subs_exception, "==============================", str(retrieve_subs_exception))
            pass


class StripeInfo(models.Model):
    subscription_price = models.DecimalField(max_digits=5, decimal_places=2)
    plan_id = models.CharField(max_length=256)

    class Meta:
        ordering = ('-pk',)

    def __str__(self):
        return 'Subscription: ${}/mon'.format(self.subscription_price)

    @classmethod
    def get_subscription_price(cls):
        try:
            return cls.objects.first().subscription_price
        except Exception as e:
            return None

    @classmethod
    def get_plan_id(cls):
        try:
            return cls.objects.first().plan_id
        except Exception as e:
            return None

    def save(self):
        if StripeInfo.objects.count() > 0:
            obj = StripeInfo.objects.first()
            if self.pk != obj.pk:
                return
        super(StripeInfo, self).save()

