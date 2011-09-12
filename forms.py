from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

attrs_dict = {'class': 'required'}

class InvitedUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2'
            ]

    first_name = forms.CharField(max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("first name"),)

    last_name = forms.CharField(max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("last name"),)

class InvitedUserCreationFormPasswordOnly(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        # fields/exlude should work, but doesn't:
        # https://code.djangoproject.com/ticket/13971
        del self.fields['username']
        self.fields.keyOrder = [
            'password1',
            'password2'
            ]

class InviteCSVForm(forms.Form):
    csv = forms.FileField()

