from django import forms
from django.contrib.auth.models import User

from japper.monitoring.plugins import iter_alert_backends
from .models import UserProfile


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email']


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        exclude = ['user', 'subscriptions']


class UserSubscriptionsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(UserSubscriptionsForm, self).__init__(*args, **kwargs)
        choices = []
        for backend in iter_alert_backends():
            for sink in backend.get_instances():
                choices.append((
                    sink.get_alert_sink_text_link(), '%s/%s' %
                    (backend.get_name(), sink.name)
                ))
        self.fields['subscriptions'] = forms.MultipleChoiceField(choices,
                required=False, widget=forms.CheckboxSelectMultiple)
