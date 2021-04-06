from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.utils.html import mark_safe
from model_utils import Choices
from django.core.files.storage import default_storage

from constant.models import ClubType


class User(AbstractUser):
    handicap = models.CharField(_('Handicap'), max_length=255, null=True, blank=True)
    photo = models.ImageField(_('Photo'), upload_to='userphotos/', null=True, blank=True)

    birthday = models.DateField(_('Birthday'), null=True, blank=True)
    location = models.CharField(_('Location'), max_length=255, null=True, blank=True)
    years_of_experience = models.IntegerField(_('Years of Experience'), default=0)
    creation_time = models.DateTimeField(_('Creation Time'), null=True, blank=True)

    @property
    def longest_distance(self):
        try:
            driver_club = self.clubs.first()
            return driver_club.avg_dist
        except Exception as e:
            return None

    @property
    def photo_url(self):
        if not self.photo:
            return ''

        if default_storage.exists(self.photo.path):
            return '%s%s' % (settings.MEDIA_URL, self.photo)
        else:
            return ''

    def image_tag(self):
        return mark_safe('<img src="%s" width="150" height="150"/>' % self.photo_url)

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


CLUB_CONFIDENCE = Choices(
        (1, 'none', _('No confidence')),
        (2, 'slight', _('Slight confidence')),
        (3, 'neutral', _('Neutral')),
        (4, 'fair', _('Fair confidence')),
        (5, 'great', _('Great confidence')),
    )


class ClubBag(models.Model):

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clubs')
    club_type = models.CharField(max_length=128)
    club_name = models.CharField(max_length=128, null=True, blank=True)
    confidence = models.PositiveSmallIntegerField(choices=CLUB_CONFIDENCE)
    avg_dist = models.PositiveIntegerField()

    class Meta:
        unique_together = ('owner', 'club_type', 'club_name', )
        ordering = ('-avg_dist', )

    def __str__(self):
        if self.club_type == 'CUSTOM':
            return self.club_name
        return self.club_type
