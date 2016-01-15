from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from crispy_forms.bootstrap import FieldWithButtons, StrictButton


class StatesSearchForm(forms.Form):

    q = forms.CharField(label='Search')

    def __init__(self, *args, **kwargs):
        super(StatesSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_action = reverse('monitoring_all_states')
        self.helper.form_class = 'navbar-form'
        self.helper.form_show_labels = False
        self.helper.form_show_errors = False
        self.helper.layout = Layout(
            FieldWithButtons(
                Field('q', placeholder='Search', css_class='search'),
                StrictButton(
                    '<span class="glyphicon glyphicon-search"></span>',
                    type='submit',
                    css_class='btn-default'
                ),
            )
        )
