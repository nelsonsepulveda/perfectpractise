from django.conf import settings

import stripe

stripe.api_key = settings.STRIPE_PRIVATE_KEY
stripe.api_version = '2018-10-31'


def create_charge(user_email, amount, token):

    try:
        resp = stripe.Charge.create(
            amount=int(amount*100),  # NOTE: amount: $1.99
            currency="usd",
            source=token,
            description="Charge for %s" % user_email
        )
    except Exception as e:
        return {
            'paid': False,
            'failure_message': str(e)
        }

    return {
        'paid': resp['paid'],  # True/False
        'failure_message': resp['failure_message']
    }


def create_customer(user_email, token):
    try:
        resp = stripe.Customer.create(
            source=token,
            description="Customer for %s" % user_email
        )

        # print("------------- create customer API -------------")
        # print(resp)
    except Exception as e:
        return {
            'created': False,
            'failure_message': str(e)
        }

    return {
        'created': True,
        'id': resp['id']
    }


def create_subscription(customer, plan):

    try:
        resp = stripe.Subscription.create(
            customer=customer,
            items=[
                {
                    "plan": plan,
                },
            ]
        )

        # print("------------- create subscription API -------------")
        # print(resp)
    except Exception as e:
        return {
            'created': False,
            'failure_message': str(e)
        }

    return {
        'created': True,
        'id': resp['id']
    }