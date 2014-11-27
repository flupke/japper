from django import forms

from .models import MonitoringSource


class MonitoringSourceForm(forms.ModelForm):

    class Meta:
        model = MonitoringSource
        exclude = []
