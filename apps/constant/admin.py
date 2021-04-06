from django.contrib import admin

from .models import *


class AimValueRangeAdmin(admin.ModelAdmin):
    list_display = ('description', 'value')


class TrajectoryValueRangeAdmin(admin.ModelAdmin):
    list_display = ('description', 'type', 'value')
    list_filter = ('type',)


class ShotImageAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'name', )
    fields = ('name', 'shape', 'image_tag')
    readonly_fields = ('image_tag',)


class ConstantAdmin(admin.ModelAdmin):
    readonly_fields = ('mode',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    class Meta:
        abstract = True


class DistanceDiffRangeAdmin(ConstantAdmin):
    pass


class AimDiffRangeAdmin(ConstantAdmin):
    pass


class TrajectoryDiffRangeAdmin(admin.ModelAdmin):
    list_display = ('description', 'value')


class PuttingDistRangeAdmin(admin.ModelAdmin):
    list_display = ('description', 'value')


class PuttingAimRangeAdmin(admin.ModelAdmin):
    list_display = ('description', 'value')


class ClubTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


admin.site.register(AimValueRange, AimValueRangeAdmin)
admin.site.register(TrajectoryValueRange, TrajectoryValueRangeAdmin)
admin.site.register(ShotImage, ShotImageAdmin)


admin.site.register(DistanceDiffRange, DistanceDiffRangeAdmin)
admin.site.register(AimDiffRange, AimDiffRangeAdmin)

admin.site.register(TrajectoryDiffRange, TrajectoryDiffRangeAdmin)
admin.site.register(PuttingDistRange, PuttingDistRangeAdmin)
admin.site.register(PuttingAimRange, PuttingAimRangeAdmin)

admin.site.register(ClubType, ClubTypeAdmin)
# Bucket Admin


class YardBucketAdmin(admin.ModelAdmin):
    list_display = ('bucket_name', 'bucket_range', 'percent',)

    def bucket_range(self, obj):
        return '%d ~ %d  (yard)' % (obj.min, obj.max)

    def bucket_name(self, obj):
        return "Bucket %d" % obj.id

    bucket_name.short_description = 'Buckets'
    bucket_range.short_description = 'Range'


class FeetBucketAdmin(admin.ModelAdmin):
    list_display = ('bucket_name', 'bucket_range', 'percent',)

    def bucket_range(self, obj):
        return '%d ~ %d  (feet)' % (obj.min, obj.max)

    def bucket_name(self, obj):
        return "Bucket %d" % obj.id

    bucket_name.short_description = 'Buckets'
    bucket_range.short_description = 'Range'


admin.site.register(YardBucket, YardBucketAdmin)
admin.site.register(FeetBucket, FeetBucketAdmin)
