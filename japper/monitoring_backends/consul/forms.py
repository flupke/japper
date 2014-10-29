from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import MonitoringSource


class MonitoringSourceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MonitoringSourceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = MonitoringSource
        exclude = []
