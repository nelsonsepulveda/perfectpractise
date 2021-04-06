from django.contrib import admin

from .models import BillingInfo, StripeInfo


class BillingInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_status', 'created', 'current_period_start', 'current_period_end')
    readonly_fields = ('user', 'subscription_status',
                       'created', 'current_period_start', 'current_period_end',
                       'customer_id', 'subscription_id', 'subscription_status',
                       'last4', 'exp_year', 'exp_month', 'brand')


admin.site.register(BillingInfo, BillingInfoAdmin)
admin.site.register(StripeInfo)
