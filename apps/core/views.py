import datetime
import pandas as pd
import json
import logging
from collections import OrderedDict

from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse

from profiles.models import ClubBag
from core.mixins import PaywallMixin
from core.models import DeltaShotReport, ScoreShotReport, Practice, PRACTICE_TYPES
from core.utils import is_full_swing, is_short_game, groupby2dict

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = 'home.html'


class ReportView(PaywallMixin, TemplateView):
    template_name = 'report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # practice sessions
        practice_id_list = Practice.objects.filter(user=user).values_list('id', flat=True)
        practice_id_list = list(OrderedDict.fromkeys(practice_id_list))

        full_swing_count = 0
        short_game_count = 0
        putting_game_count = 0

        practice_list = \
            list(DeltaShotReport.objects.filter(practice__id__in=practice_id_list)
                 .values('practice__id', 'practice__practice_type').distinct()
                 .order_by('practice__id')) + \
            list(ScoreShotReport.objects.filter(practice__id__in=practice_id_list)
                 .values('practice__id', 'practice__practice_type')
                 .distinct()
                 .order_by('practice__id'))  # NOTE: this is important because DeltaShotReport has default ordering ('practice', 'reported_at')

        for p in practice_list:
            p_type = p.get('practice__practice_type')
            if is_full_swing(p_type):
                full_swing_count += 1
            elif is_short_game(p_type):
                short_game_count += 1
            else:
                putting_game_count += 1

        context['practice_sessions'] = {
            'long': full_swing_count,
            'short': short_game_count,
            'putting': putting_game_count
        }

        context['club_list'] = ClubBag.objects.filter(owner=user).values_list('club_type', flat=True)

        # trouble shots
        context['missing_shots'] = DeltaShotReport.objects.filter(
            practice__user=user,
            hit=0
        ).order_by('-reported_at')[:5]

        return context


@require_http_methods(['POST', ])
def filter_by_daterange(request):

    def convert_delta_to_numeric(s):
        if s is None or s == '':
            return None
        elif s == 'ACCURATE':
            return 1
        else:
            return 0

    if not request.is_ajax():
        return JsonResponse({'error': 'Invalid Request'}, status=400)

    # get date range
    start_date = request.POST.get('start')
    end_date = request.POST.get('end')
    start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d 00:00:00+00:00')
    end_date = datetime.datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d 23:59:59+00:00')

    delta_shots = DeltaShotReport.objects.filter(
        practice__user=request.user,
        reported_at__range=[start_date, end_date]).exclude(delta__isnull=True).\
        order_by('reported_at')  # important

    club_shots = delta_shots.filter(
        practice__practice_type__in=[PRACTICE_TYPES.random, PRACTICE_TYPES.block, PRACTICE_TYPES.serial,
                                     PRACTICE_TYPES.custom, PRACTICE_TYPES.warmup,
                                     PRACTICE_TYPES.chip, PRACTICE_TYPES.pitch]
    )

    putting_shots = delta_shots.filter(
        practice__practice_type__in=[PRACTICE_TYPES.random_putting, PRACTICE_TYPES.standard_putting, PRACTICE_TYPES.custom_putting]
    )

    if delta_shots.count() <= 0:
        return JsonResponse({'success': False})

    club_date_range = []
    if club_shots.count() > 0:
        # delta
        df = pd.DataFrame(list(club_shots.values('reported_at', 'club', 'hit', 'distance', 'aim', 'trajectory', 'delta')))
        df = df.join(df['delta'].apply(pd.Series)).drop(columns=['delta', 'shotDescription'])

        # date range
        start = min(df['reported_at']).replace(hour=0, minute=0, second=0)
        end = max(df['reported_at'])
        step = datetime.timedelta(days=1)

        while start <= end:
            club_date_range.append(
                start.strftime("%Y-%m-%d")
            )
            start += step

        # convert to numeric
        df['reported_at'] = df['reported_at'].apply(lambda x: x.strftime("%Y-%m-%d"))
        df['distanceText'] = df['distanceText'].apply(convert_delta_to_numeric)
        df['aimText'] = df['aimText'].apply(convert_delta_to_numeric)
        df['trajectoryText'] = df['trajectoryText'].apply(convert_delta_to_numeric)

        # group by
        # df_groupby_hit = df.groupby(['club', 'reported_at']).agg({
        #     'distance': 'mean',
        #     'hit': 'mean',
        #     'distanceText': 'mean',
        # })
        df_club_hit = groupby2dict(df.groupby(['club', 'reported_at'])['hit'].agg(['mean']))
        df_club_avg_dist = groupby2dict(df.groupby(['club', 'reported_at'])['distance'].agg(['mean']))
        df_club_dist_acc = groupby2dict(df.groupby(['club', 'reported_at'])['distanceText'].agg(['mean']))
        df_club_aim_acc = groupby2dict(df.groupby(['aim', 'club', 'reported_at'])['aimText'].agg(['mean']))
        df_club_traj_acc = groupby2dict(df.groupby(['trajectory', 'club', 'reported_at'])['trajectoryText'].agg(['mean']))
    else:
        df_club_hit = {}
        df_club_avg_dist = {}
        df_club_dist_acc = {}
        df_club_aim_acc = {}
        df_club_traj_acc = {}

    put_date_range = []
    feet_range = []
    if putting_shots.count() > 0:
        df = pd.DataFrame(
            list(putting_shots.values('reported_at', 'hit', 'distance', 'trajectory', 'delta')))
        df = df.join(df['delta'].apply(pd.Series)).drop(columns=['delta', 'shotDescription'])

        start = min(df['reported_at']).replace(hour=0, minute=0, second=0)
        end = max(df['reported_at'])
        step = datetime.timedelta(days=1)

        while start <= end:
            put_date_range.append(
                start.strftime("%Y-%m-%d")
            )
            start += step

        feet_range = sorted(set(
            putting_shots.values_list('distance', flat=True)
        ))

        df['reported_at'] = df['reported_at'].apply(lambda x: x.strftime("%Y-%m-%d"))
        df['left'] = df['aimText'].apply(lambda x: 1 if x.startswith('LEFT') else 0)
        df['right'] = df['aimText'].apply(lambda x: 1 if x.startswith('RIGHT') else 0)
        df['short'] = df['distanceText'].apply(lambda x: 1 if x.startswith('SHORT') else 0)
        df['long'] = df['distanceText'].apply(lambda x: 1 if x.startswith('LONG') else 0)

        df_put_hit = groupby2dict(df.groupby(['distance', 'reported_at'])['hit'].agg(['mean']))
        df_put_left = groupby2dict(df.groupby(['distance', 'reported_at'])['left'].agg(['mean']))
        df_put_right = groupby2dict(df.groupby(['distance', 'reported_at'])['right'].agg(['mean']))
        df_put_short = groupby2dict(df.groupby(['distance', 'reported_at'])['short'].agg(['mean']))
        df_put_long = groupby2dict(df.groupby(['distance', 'reported_at'])['long'].agg(['mean']))
    else:
        df_put_hit = {}
        df_put_left = {}
        df_put_right = {}
        df_put_short = {}
        df_put_long = {}

    return JsonResponse({
        'success': True,

        'club_date_range': club_date_range,
        'hit_acc': df_club_hit,
        'avg_dist': df_club_avg_dist,
        'dist_acc': df_club_dist_acc,
        'aim_acc': df_club_aim_acc,
        'traj_acc': df_club_traj_acc,

        'put_date_range': put_date_range,
        'feet_range': feet_range,
        'put_hit': df_put_hit,
        'put_left': df_put_left,
        'put_right': df_put_right,
        'put_short': df_put_short,
        'put_long': df_put_long
    })


@require_http_methods(['POST', ])
def get_daily_activity(request):
    if not request.is_ajax():
        return JsonResponse({'error': 'Invalid Request'}, status=400)

    # get time range
    selected_date = request.POST.get('date')
    # tz_offset = int(request.POST.get('tz_offset'))
    # start_time = datetime.datetime.strptime(selected_date, '%m/%d/%Y') + datetime.timedelta(minutes=tz_offset)
    # end_time = start_time + datetime.timedelta(hours=24)

    start_time = datetime.datetime.strptime(selected_date, '%m/%d/%Y').strftime('%Y-%m-%d 00:00:00+00:00')
    end_time = datetime.datetime.strptime(selected_date, '%m/%d/%Y').strftime('%Y-%m-%d 23:59:59+00:00')

    # practice info
    practice_id_list = Practice.objects.filter(user=request.user, created_at__range=(start_time, end_time)).values_list('id', flat=True)
    practice_id_list = list(OrderedDict.fromkeys(practice_id_list))

    full_swing_count = 0
    short_game_count = 0
    putting_game_count = 0

    practice_list = \
        list(DeltaShotReport.objects.filter(practice__id__in=practice_id_list)
             .values('practice__id', 'practice__practice_type').distinct()
             .order_by('practice__id')) + \
        list(ScoreShotReport.objects.filter(practice__id__in=practice_id_list)
             .values('practice__id', 'practice__practice_type')
             .distinct()
             .order_by('practice__id'))  # NOTE: this is important because DeltaShotReport has default ordering ('practice', 'reported_at')

    for p in practice_list:
        p_type = p.get('practice__practice_type')
        if is_full_swing(p_type):
            full_swing_count += 1
        elif is_short_game(p_type):
            short_game_count += 1
        else:
            putting_game_count += 1

    # shot details filter
    shots = DeltaShotReport.objects.filter(
        practice__user=request.user,
        reported_at__range=[start_time, end_time]
    )

    total_count = shots.count()

    if total_count == 0:
        return JsonResponse({'success': False, 'no_activity': True})

    hit_count = shots.filter(hit=1).count()

    # overall accuracy
    overall_accuracy = hit_count * 100 // total_count

    # statistics analysis by pandas
    df = pd.DataFrame(list(shots.values('practice', 'reported_at', 'distance', 'club', 'hit')))

    df_groupby_hour = df.groupby(df['reported_at'].dt.hour)['hit'].agg(['sum', 'count', 'mean'])

    hour_index = list(range(0, 24))
    df_reindexed_by_hour = df_groupby_hour.reindex(hour_index, fill_value=0)

    df_groupby_club = df.groupby(df['club'])['hit'].agg(['sum', 'count', 'mean'])
    # print("df_groupby_club=====================\n", df_groupby_club)

    best_club_accuracy = df_groupby_club['mean'].max() * 100
    # print("best club percent----------------\n\n\n", df_best_club)
    # print("best club ID----------------\n\n\n", df_groupby_club['mean'].idxmax())
    best_club_name = df_groupby_club['mean'].idxmax()

    ## practice info
    # df_groupby_practice = df.groupby(df['practice'])['practice'].agg(['count'])  # NOTE: order by practice ID
    # print("df_groupby_practice------------------\n\n\n", df_groupby_practice)
    #
    # practice_ids = df_groupby_practice.index.values
    # practice_names = Practice.objects.filter(id__in=practice_ids).values('id', 'practice_type')
    # for p in practice_names:
    #     p.update({'name': PRACTICE_TYPES[p['practice_type']]})
    # print(practice_names)

    max_dist = df['distance'].max()
    # print("max---------------\n\n\n", max_dist)

    data = {
        'overall_accuracy': overall_accuracy,
        'data_by_hour': json.loads(df_reindexed_by_hour.to_json(orient='split')),
        'data_by_club': json.loads(df_groupby_club.to_json(orient='index')),
        'best_club': {
            'name': best_club_name,
            'accuracy': int(best_club_accuracy),
        },

        'max_dist': int(max_dist),
        'practice_info': {
            'long': full_swing_count,
            'short': short_game_count,
            'putting': putting_game_count
        }
    }

    return JsonResponse({'success': True, 'daily_activity': data})
