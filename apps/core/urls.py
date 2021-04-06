from django.urls import path
from core.views import HomeView, ReportView, \
    filter_by_daterange, get_daily_activity

app_name = 'core'

urlpatterns = [

    path('', HomeView.as_view(), name='home'),
    path('report/', ReportView.as_view(), name='report'),
    path('filter_by_daterange/', filter_by_daterange),
    path('get_daily_activity/', get_daily_activity),
]
