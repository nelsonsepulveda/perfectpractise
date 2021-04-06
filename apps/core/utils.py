from django.conf import settings
import random
import pycountry
import numpy as np

from constant.models import YardBucket, FeetBucket
from core.models import PRACTICE_TYPES, DeltaShotReport, Practice
from profiles.models import ClubBag

def pick_random_distances(putting=False, practice=None, driver=None, clubs=None):
    # get existing dist_list
    # --- e.g: 75, 128, 103, 155, 189, 140, 170, 105, 200, 240, 85, 110, 185, 133, 160, 350, 70, 162, 120, 130
    if practice is None:
        existing_dist_list = []
    else:
        existing_dist_list = DeltaShotReport.objects.filter(practice=practice).values_list('distance', flat=True)
        if len(existing_dist_list) > 0:
            existing_dist_list = list(set(existing_dist_list))

    # pick_number e.g: [1,2,2,2,1,1,2]
    if putting:
        buckets = FeetBucket.objects.all()
    else:
        buckets = YardBucket.objects.all()

    # get new distance in every bucket
    new_dist = {}
    final_dist_list = []
    clubs_list = clubs.all()
    club_dist_list = []
    rest_dist_list = []

    if len(clubs.all()):
        for club in reversed(clubs_list):
            club_dist_list.append(club.avg_dist)
        for i in range(len(club_dist_list)-1):
            random_choose_dist = random.choice(list(range(club_dist_list[i], club_dist_list[i+1])))
            if random_choose_dist >= 75:
                rest_dist_list.append(random_choose_dist)

    for bucket in buckets:
        new_dist[bucket.pk] = bucket.pick_dists(existing_dist_list, driver)

    # randomize by bucket order
    bucket_order = list(buckets.values_list('pk', flat=True))
    random.shuffle(bucket_order)

    while True:
        old_count = len(final_dist_list)
        for bucket_pk in bucket_order:
            try:
                final_dist_list.append(new_dist[bucket_pk].pop())
            except IndexError:  # pop from empty list
                pass
        if len(final_dist_list) >= settings.PICK_COUNT:
            break
        if len(final_dist_list) == old_count:  # not be appended anymore
            break

    final_dist_list = final_dist_list + rest_dist_list
    random.shuffle(final_dist_list)

    # if length > PICK_COUNT, randomly pop
    _length = len(final_dist_list)
    if _length > settings.PICK_COUNT:
        poped_random_index_list = random.sample(range(_length), _length - settings.PICK_COUNT)
        poped_random_index_list.sort(reverse=True)
        for index in poped_random_index_list:
            final_dist_list.pop(index)

    return final_dist_list


def pick_standard_putts(practice=None):
    if practice is None:
        existing_dist_list = []
    else:
        existing_dist_list = practice.get_existing_dist_list()

    buckets = FeetBucket.objects.filter(max__lte=25)  # NOTE: hardcode 25
    # get new distance in every bucket
    new_dist = {}
    for bucket in buckets:
        new_dist[bucket.pk] = bucket.pick_standard_dists(existing_dist_list)

    # randomize by bucket order
    bucket_order = list(buckets.values_list('pk', flat=True))
    random.shuffle(bucket_order)

    final_dist_list = []
    for bucket_pk in bucket_order * 3:  # NOTE: hardcoded 3.
        try:
            final_dist_list.append(new_dist[bucket_pk].pop())

        except IndexError:  # pop from empty list
            pass

    # if length > PICK_COUNT, randomly pop
    _length = len(final_dist_list)
    if _length > settings.PICK_COUNT:
        poped_random_index_list = random.sample(range(_length), _length - settings.PICK_COUNT)
        for index in poped_random_index_list:
            final_dist_list.pop(index)

    return final_dist_list


def pick_chip_distances(practice=None):
    return random.sample(set(range(5, 25)), 10)


def pick_pitch_distances(practice=None):
    return random.sample(set(range(25, 75)), 10)


def get_blocked_bin(user=None):
    """
    :return: bin for block practice. NOTE: first bin (check again later.)
    """
    if user is None:
        return None

    bin_list = YardBucket.get_hist_bin()
    practice_list = Practice.objects.filter(
        user=user,
        practice_type__in=[PRACTICE_TYPES.random, PRACTICE_TYPES.block, PRACTICE_TYPES.serial, PRACTICE_TYPES.custom]
    )

    block_bin = None
    yards = YardBucket.objects.all()

    for yard in yards:
        all_shots1 = DeltaShotReport.objects.filter(
            practice__in=practice_list).filter(distance__in=range(yard.min, yard.max)).order_by("-reported_at")
        all_shots = all_shots1[0:10]
        all_dists = [shot.distance for shot in all_shots]
        hit_dists = [shot.distance for shot in all_shots if shot.hit == 0]

        total_hist, bins = np.histogram(all_dists, bins=bin_list)
        hit_hist, bins = np.histogram(hit_dists, bins=bin_list)

        for h, t, b in zip(hit_hist, total_hist, bin_list):
            if t != 0:
                if t < 10 or h / t < 0.3:
                    continue

                # if len(hit_dists):
                #     if sum(hit_dists) / len(hit_dists) > 224:
                #         block_bin = YardBucket.objects.get(min=196)
                #         break

                block_bin = YardBucket.objects.get(min=b)
                break

        if block_bin is not None:
            break

    return block_bin


def pick_custom_distances(min, max):
    if min == max:
        return [min for i in range(10)]
    try:
        dist_set = list(range(min, max+1))
        if len(dist_set) < 10:
            dist_set = (10//len(dist_set) + 1) * dist_set
        return random.sample(dist_set, 10)
    except ValueError as e:
        return []


def is_full_swing(p_type):
    """
    :param p_type: practice_type
    :return: True/False
    """
    if p_type in [PRACTICE_TYPES.random, PRACTICE_TYPES.warmup,
                  PRACTICE_TYPES.serial, PRACTICE_TYPES.block,
                  PRACTICE_TYPES.custom]:
        return True
    else:
        return False


def is_short_game(p_type):
    """
    :param p_type: practice_type
    :return: True/False
    """
    if p_type in [PRACTICE_TYPES.chip, PRACTICE_TYPES.pitch]:
        return True
    else:
        return False


def get_country_list():
    """Return a list of ISO 3166-1 Alpha 2 country codes."""

    countries0 = [(x.alpha_2, x.name)for x in pycountry.countries]
    countries_sorted = sorted(countries0, key=lambda x: x[1])
    country_list = [
        ("", "--- Select country ---"),
    ]
    country_list.extend(countries_sorted)
    return country_list


def groupby2dict(grouped_df):
    levels = len(grouped_df.index.levels)
    dicts = [{} for i in range(levels)]
    last_index = None

    for index, value in grouped_df.itertuples():

        if not last_index:
            last_index = index

        for (ii, (i, j)) in enumerate(zip(index, last_index)):
            if not i == j:
                ii = levels - ii - 1
                dicts[:ii] = [{} for _ in dicts[:ii]]
                break

        for i, key in enumerate(reversed(index)):
            dicts[i][key] = value
            value = dicts[i]

        last_index = index

    return dicts[-1]
