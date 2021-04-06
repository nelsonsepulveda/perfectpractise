from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse

from .forms import ProfileEditForm
from .models import User


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'profiles/profile.html'
    form_class = ProfileEditForm
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('pk', 0)
        try:
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            return None

    def get_success_url(self):
        return reverse('profile', kwargs={'pk': self.object.pk})


