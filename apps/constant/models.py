from django.db import models
from django.conf import settings
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
import random


class AimValueRange(models.Model):
    description = models.CharField(max_length=64, unique=True)
    value = models.IntegerField(unique=True)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('value',)

    @property
    def is_draw(self):
        return self.value < 0

    @property
    def is_straight(self):
        return self.value == 0

    @property
    def is_fade(self):
        return self.value > 0


class TrajectoryValueRange(models.Model):
    TYPES = (
        ('long', 'Long'),
        ('putting', 'Putting'),
        ('chip', 'Around the Green (chip)'),
        ('pitch', 'Around the Green (pitch)'),
    )

    description = models.CharField(max_length=64)
    value = models.IntegerField()
    type = models.CharField(max_length=10, choices=TYPES, default='long')

    def __str__(self):
        return self.description

    def is_long(self):
        return self.type == 'long'

    def is_putting(self):
        return self.type == 'putting'

    class Meta:
        ordering = ('type',)
        unique_together = ('type', 'description')


class ShotImage(models.Model):
    name = models.CharField(max_length=64, unique=True)
    shape = models.ImageField('Shot Shape', upload_to='shotshapes/')

    def __str__(self):
        return self.get_url()

    class Meta:
        ordering = ('name',)

    def get_url(self):
        return '%s%s' % (settings.MEDIA_URL, self.shape)

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.get_url())
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class AbstractDiffRange(models.Model):
    min = models.IntegerField()
    step = models.PositiveIntegerField()
    max = models.IntegerField()
    mode = models.CharField(max_length=10, choices=(('yard', 'Yard'), ('feet', 'Feet')), default='yard')

    class Meta:
        abstract = True

    def __str__(self):
        return ' %s ~ %s (%s)  |  step: %s' % (self.min, self.max, self.mode, self.step)


class DistanceDiffRange(AbstractDiffRange):
    pass


class AimDiffRange(AbstractDiffRange):
    pass


class TrajectoryDiffRange(models.Model):
    description = models.CharField(max_length=50, unique=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('value',)


# ----------------
#   Bucket model
# ----------------
class AbstractBucket(models.Model):
    class Meta:
        abstract = True
        ordering = ('min',)
        unique_together = ('min', 'max')

    min = models.IntegerField(unique=True, verbose_name='from')
    max = models.IntegerField(unique=True, verbose_name='to')
    percent = models.IntegerField(verbose_name='percent (%)')

    def is_in_bucket(self, distance):
        """
        :param distance:
        :return: check if 'distance' is in this bucket
        """
        if self.min <= distance <= self.max:
            return True
        else:
            return False

    @property
    def mid(self):
        return self.min + (self.max - self.min) // 2

    def pick_dists(self, excepted_dist_list=None, max_limit=None):
        """
        :param excepted_dist_list:
        :param max_limit: All of the picked distances should not be greater than max_limit.
        :return: pick distances in this bucket except of param: except_dist_set
        """
        picked_count = settings.PICK_COUNT  # round(settings.PICK_COUNT * self.percent / 100)
        if max_limit is None:
            all_dist = range(self.min, self.max+1)
        else:
            if self.min > max_limit:
                return []
            elif self.max > max_limit:  # cij_changed
                all_dist = range(self.min, max_limit+1)
            else:
                all_dist = range(self.min, self.max+1)  # fixed for spread more evenly

        diff_list = list(set(all_dist) - set(excepted_dist_list))

        try:
            if diff_list is None:  # first pick OR all such distances have been included in the practice
                count = picked_count if len(all_dist) >= picked_count else len(all_dist)
                return random.sample(all_dist, count)

            elif len(diff_list) >= picked_count:
                return random.sample(diff_list, picked_count)

            else:  # len(diff_list) < picked_count
                new_list = list(set(all_dist) - set(diff_list))
                new_count = picked_count - len(diff_list) if picked_count - len(diff_list) < len(new_list) else len(new_list)
                return diff_list + random.sample(
                    new_list,
                    new_count
                )
        except Exception:
            return []

    @classmethod
    def get_bucket_obj(cls, distance):
        """
        :param distance:
        :return: bucket obj which contains the param:distance
        """
        for obj in cls.objects.all():
            if obj.is_in_bucket(distance):
                return obj
        return None

    @classmethod
    def get_pick_count_list(cls):
        pick_count_list = []
        for obj in cls.objects.all():
            _number = round(settings.PICK_COUNT * obj.percent / 100)  # NOTE: should not be less than 5%
            pick_count_list.append(_number)
        return pick_count_list

    @classmethod
    def get_hist_bin(cls):
        """
        :return: bin for histogram analysis
        """
        hist_bin = []
        for obj in cls.objects.all():
            hist_bin.append(obj.min)
        hist_bin.append(obj.max)  # At this line, obj is last object.

        return hist_bin


class YardBucket(AbstractBucket):
    """
    Bucket for Non-Putting Mode
    """

    def __str__(self):
        return '%d ~ %d (yard)' % (self.min, self.max)


class FeetBucket(AbstractBucket):
    """
    Bucket for Putting Mode
    """

    def __str__(self):
        return '%d ~ %d (feet)' % (self.min, self.max)

    def pick_standard_dists(self, excepted_dist_list=None):
        """
        :param excepted_dist_list:
        :return: similar to "pick_dists" function, difference percent + 5%(hardcode)
        """
        picked_count = round(settings.PICK_COUNT * (self.percent + 5) / 100)
        all_dist = range(self.min, self.max + 1)
        diff_list = list(set(all_dist) - set(excepted_dist_list))

        if diff_list is None:  # first pick OR all such distances have been included in the practice
            return random.sample(all_dist, picked_count)

        elif len(diff_list) >= picked_count:
            return random.sample(diff_list, picked_count)

        else:  # len(diff_list) < picked_count
            return diff_list + random.sample(
                list(set(all_dist) - set(diff_list)),
                picked_count - len(diff_list)
            )


class ClubType(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id', )


class PuttingAimRange(models.Model):
    description = models.CharField(max_length=50, unique=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('value',)


class PuttingDistRange(models.Model):
    description = models.CharField(max_length=50, unique=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('value',)


# --- Warmup practice list ---
# NOTE: hardcode

WARMUP_PRACTICE_LIST = [
    # 1
    [
        {'dist': 85},
        {'dist': 135},
        {'dist': 155},
        {'dist': 155},
        {'dist': 105},
        {'dist': 145},
        {'dist': 165},
        {'dist': 165}
    ],

    # 2
    [
        {'dist': 125, 'traj': 'High'},
        {'dist': 125, 'traj': 'Low'},
        {'dist': 145, 'aim': 'Fade'},
        {'dist': 145, 'aim': 'Draw'},
        {'dist': 165, 'aim': 'Straight'},
        {'dist': 135, 'aim': 'Draw'},
        {'dist': 135, 'aim': 'Fade'},
        {'dist': 'Driver'},
        {'dist': 'Driver'}
    ],

    # 3
    [
        {'dist': 75},
        {'dist': 125},
        {'dist': 150, 'aim': 'Draw'},
        {'dist': 150, 'aim': 'Fade'},
        {'dist': 105},
        {'dist': 150, 'aim': 'Draw'},
        {'dist': 150, 'aim': 'Fade'},
    ],

    # 4
    [
        {'dist': 75},
        {'dist': 125},
        {'dist': 155},
        {'dist': 85},
        {'dist': 135},
        {'dist': 165},
        {'dist': 95},
        {'dist': 145}
    ]
]
