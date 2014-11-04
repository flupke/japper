from django import forms

from .models import AlertSink


class AlertSinkForm(forms.ModelForm):

    class Meta:
        model = AlertSink
        exclude = []

