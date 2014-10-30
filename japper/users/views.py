from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from vanilla import GenericView

from .forms import UserForm, UserProfileForm


class UpdateUserProfile(GenericView):

    template_name = 'users/profile.html'

    def get_forms(self, request, data=None):
        user_form = UserForm(data=data, instance=request.user)
        user_profile_form = UserProfileForm(data=data,
                instance=request.user.profile)
        return user_form, user_profile_form

    def get(self, request):
        user_form, user_profile_form = self.get_forms(request)
        context = self.get_context_data(user_form=user_form,
                user_profile_form=user_profile_form)
        return self.render_to_response(context)

    def post(self, request):
        user_form, user_profile_form = self.get_forms(request, request.POST)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            return HttpResponseRedirect(reverse('users_profile'))
        context = self.get_context_data(user_form=user_form,
                user_profile_form=user_profile_form)
        return self.render_to_response(context)
