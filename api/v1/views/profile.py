from django.conf import settings
import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework import generics
import pytz
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from api.v1.serializers import ProfileSerializer, RegisterSerializer

from billing.models import BillingInfo, StripeInfo

from oauth2_provider.models import get_application_model
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, OAuth2Authentication
import stripe
import json
import math

stripe.api_key = settings.STRIPE_PRIVATE_KEY
stripe.api_version = '2018-02-28'

Client = get_application_model()
User = get_user_model()


class ProfileRegisterView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny, ]

    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)

        # Check format and unique constraint
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        user = serializer.save()

        # create OAUTH2 client
        client = Client(
            user=user,
            name=user.username,
            redirect_uris='',

            client_id=user.username,
            client_secret='',

            client_type=Client.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Client.GRANT_PASSWORD,
        )
        client.save()

        return Response({'username': user.username, 'client_id': user.username}, status=status.HTTP_201_CREATED)


class ProfileViewSet(generics.RetrieveUpdateAPIView):
    """
    Get/Update Profile

    - subscription_status
        * 0: not subscribed
        * 1: subscribed and active
        * 2: subscribed but inactive
    """
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class CheckTrialView(APIView):
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        if request.user.creation_time is None:
            return Response({'error': 'Creation time is None'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            max_trial_time_seconds = 604800
            creation_time_by_second = math.floor(request.user.creation_time.timestamp())
            current_time_by_second = math.floor(datetime.datetime.now().timestamp())
            trial_expiry_time_seconds = max_trial_time_seconds - (current_time_by_second - creation_time_by_second)
            if trial_expiry_time_seconds < 0:
                return Response({'trial_expiry_time_seconds': 0})

            return Response({'trial_expiry_time_seconds': trial_expiry_time_seconds})


class BillingRegisterView(APIView):
    """
    Required param

    - stripeToken (required)


    Response code
    * 200, 201: created subscription successfully
    * 400, 403: failed
    """
    authentication_classes = [OAuth2Authentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        # check stripe configuration
        plan_id = StripeInfo.get_plan_id()

        if plan_id is None:
            return Response({'error': 'Plan is not defined yet in backend'}, status=status.HTTP_403_FORBIDDEN)

        # --- create/update customer ---
        user = request.user

        received_json_data = json.loads(request.body.decode('utf-8'))
        # stripe_token = request.POST.get('stripeToken', None)

        stripe_token = received_json_data.get('stripeToken', None)

        if stripe_token is None:
            return Response({"Invalid request": 'stripeToken is required'}, status=status.HTTP_400_BAD_REQUEST)

        billing_obj, created = BillingInfo.objects.get_or_create(user=user)

        try:
            if billing_obj.customer_id is None:
                # create customer
                cus_resp = stripe.Customer.create(
                    source=stripe_token,
                    email=user.email
                )
            else:
                # retrive customer
                try:
                    cus_resp = stripe.Customer.retrieve(billing_obj.customer_id)
                    cus_resp.source = stripe_token
                    cus_resp.save()

                except stripe.error.InvalidRequestError:  # InvalidRequestError ('No such customer: 123456',)
                    # create customer
                    cus_resp = stripe.Customer.create(
                        source=stripe_token,
                        email=user.email
                    )

            billing_obj.customer_id = cus_resp['id']

        except Exception as create_cus_exception:
            return Response({"Invalid request": str(create_cus_exception)}, status=status.HTTP_400_BAD_REQUEST)

        # --- create/update subscription ---
        if billing_obj.subscription_id is not None:
            billing_obj.save()
            return Response(status=status.HTTP_200_OK)

        try:
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
            billing_obj.current_period_start = datetime.datetime.fromtimestamp(subs_resp['current_period_start'], tz=pytz.UTC)
            billing_obj.current_period_end = datetime.datetime.fromtimestamp(subs_resp['current_period_end'], tz=pytz.UTC)

            billing_obj.save()

            return Response(status=status.HTTP_201_CREATED)

        except Exception as create_subs_exception:
            return Response({"Invalid request": str(create_subs_exception)}, status=status.HTTP_400_BAD_REQUEST)


