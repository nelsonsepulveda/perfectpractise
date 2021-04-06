from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import User, ClubBag


class ClubBagInline(admin.TabularInline):
    model = ClubBag


class UserAdmin(BaseUserAdmin):
    inlines = [
        ClubBagInline,
    ]
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'photo', 'image_tag', 'handicap', 'birthday', 'location', 'years_of_experience', 'creation_time')}),
        # (_('Personal info'), {'fields': ()}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ('image_tag',)


admin.site.register(User, UserAdmin)
