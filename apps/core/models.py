from django.db import models
from django.db.models import Sum
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

from constant.models import ShotImage, DistanceDiffRange, AimValueRange, AimDiffRange, \
    TrajectoryValueRange, TrajectoryDiffRange, YardBucket, FeetBucket, ClubType


PRACTICE_TYPES = Choices(

        # --- full swing ---

        (0, 'random', _('Full Swing (Gated Random)')),  # gated random practice
        (1, 'serial', _('Serial')),
        (2, 'block', _('Block')),
        (3, 'warmup', _('Warmup')),
        (8, 'custom', _('Custom Practice')),


        # --- putting ---

        (4, 'random_putting', _('Putting (Gated Random )')),
        (5, 'standard_putting', _('Putting (Standard)')),
        (9, 'custom_putting', _('Putting (Custom)')),
        (22, 'within_3feet', _('Putting (Within 3 Feet)')),
        (23, 'challenge_6foot', _('Putting (6 Foot Challenge)')),


        # --- around the green ---

        (6, 'chip', _('Around the green (Chip)')),
        (7, 'pitch', _('Around the green (Pitch)')),
    )


class Practice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="practices")
    practice_type = models.PositiveSmallIntegerField(choices=PRACTICE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    # distance range
    min_dist = models.PositiveIntegerField(null=True, blank=True)
    max_dist = models.PositiveIntegerField(null=True, blank=True)

    # @property
    # def is_full_swing(self):
    #     if self.practice_type in [PRACTICE_TYPES.random, PRACTICE_TYPES.warmup,
    #                               PRACTICE_TYPES.serial, PRACTICE_TYPES.block,
    #                               PRACTICE_TYPES.custom]:
    #         return True
    #     else:
    #         return False
    #
    # @property
    # def is_short_game(self):
    #     if self.practice_type in [PRACTICE_TYPES.chip, PRACTICE_TYPES.pitch]:
    #         return True
    #     else:
    #         return False

    @property
    def is_valid(self):
        try:
            if self.reports.count() > 0:
                return True
        except Exception:
            pass

        return False

    @property
    def reports(self):
        if self.practice_type in [PRACTICE_TYPES.standard_putting,
                                  PRACTICE_TYPES.within_3feet,
                                  PRACTICE_TYPES.challenge_6foot]:
            return ScoreShotReport.objects.filter(practice=self)
        else:
            return DeltaShotReport.objects.filter(practice=self)

    @property
    def max_score(self):
        if self.practice_type in [PRACTICE_TYPES.standard_putting,
                                  PRACTICE_TYPES.within_3feet,
                                  PRACTICE_TYPES.challenge_6foot]:
            return 250  # NOTE: hardcode
        else:
            return DeltaShotReport.objects.filter(practice=self).count()

    @property
    def score(self):
        try:
            if self.practice_type in [PRACTICE_TYPES.standard_putting, PRACTICE_TYPES.within_3feet, PRACTICE_TYPES.challenge_6foot]:
                shots = ScoreShotReport.objects.filter(practice=self).aggregate(Sum('points'))
                return shots['points__sum']
            else:
                shots = DeltaShotReport.objects.filter(practice=self).aggregate(Sum('hit'))
                return shots['hit__sum']
        except Exception:
            return 0

    class Meta:
        ordering = ('-created_at', )


class DeltaShotReport(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)

    distance = models.PositiveIntegerField()
    aim = models.CharField(max_length=64, null=True, blank=True)
    trajectory = models.CharField(max_length=64, null=True, blank=True)
    club = models.CharField(max_length=128, null=True, blank=True)

    delta = JSONField(help_text='Delta and Advanced Shot Reporting')

    hit = models.PositiveSmallIntegerField(choices=((1, 'Hit'), (0, 'Miss')))

    class Meta:
        ordering = ('practice', 'reported_at',)


class ScoreShotReport(models.Model):
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)

    distance = models.PositiveIntegerField(null=True, blank=True)
    putt_counts = models.PositiveSmallIntegerField(help_text='putt counts required')
    points = models.IntegerField()

    class Meta:
        ordering = ('practice', 'reported_at',)
