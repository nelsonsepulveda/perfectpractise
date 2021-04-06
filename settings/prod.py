from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '13.56.194.183',
    'ec2-13-56-194-183.us-west-1.compute.amazonaws.com',
    '*'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'golf_db',
        'USER': 'golf',
        'PASSWORD': 'alfyk6Q9yxSj',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# Stripe
# -- live
STRIPE_PUBLIC_KEY = 'pk_test_KsJjZ6YJhTvObzLbCU38TnVt'
STRIPE_PRIVATE_KEY = 'sk_test_qfVcV8RPdZeMGcmnFypKB40E'

# Email setting
DEFAULT_FROM_EMAIL = 'no-reply@pp.com'
DEFAULT_TO_EMAIL = 'hugh.d.myers+1@gmail.com'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'osinov'
EMAIL_HOST_PASSWORD = 'Gm66!+fCdaKU/}s'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
