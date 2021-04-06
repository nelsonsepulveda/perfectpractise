import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'doqq3r=61g&v@um65a(9&e4r4y&+6)-pnf=^_jlq^cc_y&^td$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# add new path for apps
os.sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # installed packaged
    'django_extensions',
    'oauth2_provider',
    'rest_framework',
    'rest_framework_swagger',
    'admin_reorder',
    'django_cleanup',
    'rangefilter',

    'drf_yasg',

    # inner apps
    'core',
    'billing',
    'constant',
    'profiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'admin_reorder.middleware.ModelAdminReorder',
]


ROOT_URLCONF = 'urls'

# user settings
AUTH_USER_MODEL = 'profiles.User'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'core:report'
LOGOUT_REDIRECT_URL = 'core:home'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'apps/assets'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# rest framework

OAUTH2_PROVIDER = {
    'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore',
    'REFRESH_TOKEN_EXPIRE_SECONDS': 3600 * 24,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600 * 24,
    'OAUTH_SINGLE_ACCESS_TOKEN': True,
    'OAUTH_DELETE_EXPIRED': True,
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope', }
 }

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
#         'rest_framework.authentication.SessionAuthentication'  # browsable api
#     ),
#
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     )
# }


# customize admin page

ADMIN_REORDER = (
    # Buckets
    {
        'app': 'constant',
        'label': 'Buckets',
        'models': ('constant.YardBucket', 'constant.FeetBucket')},

    # Value (Aim, Trajectory)
    {
        'app': 'constant',
        'label': 'Constant Values',
        'models': (
            'constant.ShotImage',
            'constant.AimValueRange',
            'constant.TrajectoryValueRange',
        )
    },

    # Diff (Distance, Aim, Trajectory)
    {
        'app': 'constant',
        'label': 'Constant Diff',
        'models': (
            'constant.DistanceDiffRange',
            'constant.AimDiffRange',
            'constant.TrajectoryDiffRange',
            'constant.PuttingAimRange',
            'constant.PuttingDistRange',
        )
    },

    # club
    {
        'app': 'constant',
        'label': 'Club Type',
        'models': (
            'constant.ClubType',
        )
    },

    # payment
    {
        'app': 'billing',
        'label': 'Billing',
        'models': (
            'billing.StripeInfo',
            'billing.BillingInfo'
        )
    },

    # customer, reports, Practice
    {
        'app': 'core',
        'label': 'Golf Practice',
        'models': (
            'core.Practice',
        )
    },

    # Authorization
    {
        'app': 'auth',
        'label': 'Users',
        'models': (
            # {'model': 'auth.User', 'label': 'Staff'},
            'profiles.User',
            'auth.Group',
        )
    },

    # oauth2_provider
    {
        'app': 'oauth2_provider',
        'label': 'Oauth2',
        'models': (
            'oauth2_provider.Application',
            'oauth2_provider.AccessToken',
            'oauth2_provider.RefreshToken',
        )
    },

)


# Criteria
LONG_GAME_MIN_DISTANCE = 75  # (yards)
DIST_FOR_SHAPE = 125
PICK_COUNT = 10


# Stripe
# -- dev
STRIPE_PUBLIC_KEY = '...'
STRIPE_PRIVATE_KEY = '...'


# Email setting
DEFAULT_FROM_EMAIL = 'perfect_practice@example.com'
