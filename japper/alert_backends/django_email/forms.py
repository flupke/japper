from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import AlertSink


class AlertSinkForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AlertSinkForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = AlertSink
        exclude = []

