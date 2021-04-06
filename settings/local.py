from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'debug_toolbar',
    # 'silk',
]

# Database

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'golf_db',
    #     'USER': 'postgres',
    #     'PASSWORD': '',
    #     'HOST': 'localhost',
    #     'PORT': '5432'
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'golf_db_prod',
        'USER': 'golf',
        'PASSWORD': 'alfyk6Q9yxSj',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'silk.middleware.SilkyMiddleware',
]

INTERNAL_IPS = ['127.0.0.1', 'localhost', '192.168.2.26']

# Stripe
STRIPE_PUBLIC_KEY = 'pk_test_KsJjZ6YJhTvObzLbCU38TnVt'
STRIPE_PRIVATE_KEY = 'sk_test_qfVcV8RPdZeMGcmnFypKB40E'

# Email setting
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# # Logging
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'logs/debug.log')
#         }
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True
#         },
#     },
# }
