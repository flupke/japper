from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from vanilla import GenericView

from .forms import UserForm, UserProfileForm, UserSubscriptionsForm


class UpdateUserProfile(GenericView):

    template_name = 'users/profile.html'

    def get_forms(self, request, data=None):
        user_form = UserForm(data=data, instance=request.user)
        profile_form = UserProfileForm(data=data,
                instance=request.user.profile)
        subscriptions_form = UserSubscriptionsForm(data=data,
                initial={'subscriptions': request.user.profile.subscriptions.split()})
        return user_form, profile_form, subscriptions_form

    def get(self, request):
        user_form, profile_form, subscriptions_form = self.get_forms(request)
        context = self.get_context_data(user_form=user_form,
                profile_form=profile_form,
                subscriptions_form=subscriptions_form)
        return self.render_to_response(context)

    def post(self, request):
        user_form, profile_form, subscriptions_form = self.get_forms(request,
                request.POST)
        if (user_form.is_valid() and profile_form.is_valid() and
                subscriptions_form.is_valid()):
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.subscriptions = ' '.join(
                    subscriptions_form.cleaned_data['subscriptions'])
            profile.save()
            return HttpResponseRedirect(reverse('users_profile'))
        context = self.get_context_data(user_form=user_form,
                profile_form=profile_form,
                subscriptions_form=subscriptions_form)
        return self.render_to_response(context)
