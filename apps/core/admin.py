from django.contrib import admin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from .models import Practice, ScoreShotReport, DeltaShotReport


class ScoreShotsInline(admin.TabularInline):
    model = ScoreShotReport
    extra = 0


class DeltaShotsInline(admin.TabularInline):
    model = DeltaShotReport
    extra = 0


class PracticeAdmin(admin.ModelAdmin):
    inlines = [DeltaShotsInline, ScoreShotsInline]
    list_display = ('user', 'practice_type', 'created_at', 'is_valid', 'min_dist', 'max_dist')
    list_filter = ('practice_type', ('created_at', DateRangeFilter))


admin.site.register(Practice, PracticeAdmin)
