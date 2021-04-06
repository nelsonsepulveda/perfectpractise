from django.conf.urls import url, include

from .views import *

import oauth2_provider.views as oauth2_views

# OAuth2 provider endpoints
oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

urlpatterns = [

    # pricing Info
    url(r'^pricing/$', PricingInfoView.as_view()),
    url(r'^pricing/register/$', BillingRegisterView.as_view()),

    # profile
    url(r'^profile/$', ProfileViewSet.as_view()),

    # trial_expiry_time_seconds
    url(r'^check_trial/$', CheckTrialView.as_view()),

    # register
    url(r'^register/$', ProfileRegisterView.as_view()),

    # constant
    url(r'^constant/practice_type/$', PracticeTypeListView.as_view()),
    # url(r'^constant/club_type/$', ClubTypeListView.as_view()),

    # practice

    url(r'^practice/gated_random/(?P<practice_id>\d+)/$', GatedRandomPracticeView.as_view()),
    url(r'^practice/warmup/$', WarmupPracticeView.as_view()),
    url(r'^practice/serial/$', SerialPracticeView.as_view()),
    url(r'^practice/block/$', BlockPracticeView.as_view()),
    url(r'^practice/custom/(?P<practice_id>\d+)/$', CustomPracticeView.as_view()),

    url(r'^practice/putting_random/(?P<practice_id>\d+)/$', PuttingRandomPracticeView.as_view()),
    url(r'^practice/putting_custom/(?P<practice_id>\d+)/$', CustomPuttingView.as_view()),
    url(r'^practice/putting_standard/$', StandardPuttingView.as_view()),

    url(r'^practice/pitch/(?P<practice_id>\d+)/$', PitchPracticeView.as_view()),
    url(r'^practice/chip/(?P<practice_id>\d+)/$', ChipPracticeView.as_view()),


    # report
    url(r'^report/practice/(?P<practice_id>\d+)/$', DeltaReportView.as_view()),
    url(r'^report/scorecard/$', ScoreCardReportView.as_view()),

    url(r'^history/list/$', HistoryListView.as_view()),
    url(r'^history/detail/(?P<practice_id>\d+)/$', HistoryDetailView.as_view()),

    # diff range
    url(r'^diff_range/distance/$', DistanceDiffList.as_view()),
    url(r'^diff_range/aim/$', AimDiffList.as_view()),
    url(r'^diff_range/trajectory/$', TrajectoryDiffList.as_view()),
    url(r'^diff_range/putting/$', PuttingDiffView.as_view()),

    # oauth2
    url(r'^o/', include(oauth2_endpoint_views)),
]
