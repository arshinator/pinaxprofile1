from django import forms
from django.forms.extras.widgets import SelectDateWidget

import account.forms
from django.utils.translation import ugettext_lazy as _

class SignupForm(account.forms.SignupForm):

    birthdate = forms.DateField(
    label=_("birthdate"),
    widget=SelectDateWidget(years=range(1910, 1991)))

class SettingsForm(account.forms.SettingsForm):

    birthdate = forms.DateField(
    label=_("birthdate"),
    widget=SelectDateWidget(years=range(1910, 1991))
    ,required=True)
