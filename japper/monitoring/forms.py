from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout


class StatesSearchForm(forms.Form):

    q = forms.CharField(label='Search')

    def __init__(self, *args, **kwargs):
        super(StatesSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_action = reverse('monitoring_all_states')
        self.helper.form_class = 'navbar-form'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'q',
            Submit('submit', 'Go'),
        )
