from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


urlpatterns = [
    url('', include('core.urls')),
    url(r'^account/', include('profiles.urls')),
    url(r'^billing/', include('billing.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include('api.v1.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Change admin site title
admin.site.site_header = _("Perfect Practice Administration")
admin.site.site_title = _("Golf App Admin")


schema_view = get_schema_view(
   openapi.Info(
      title="Perfect Practice API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="champion_327@hotmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   validators=['flex', 'ssv'],
   public=True,
   permission_classes=(AllowAny,),
)

urlpatterns += [
   url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
   url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
   url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        # url(r'^silk/', include('silk.urls', namespace='silk'))
    ] + urlpatterns
