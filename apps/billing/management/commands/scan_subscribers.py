from django.core.management.base import BaseCommand

from billing.models import BillingInfo


class Command(BaseCommand):
    help = "My shiny new management command."

    # def add_arguments(self, parser):
    #     parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        subscribers = BillingInfo.objects.filter(subscription_id__isnull=False)
        for sb in subscribers:
            sb.get_update_from_stripe()
