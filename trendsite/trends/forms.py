from django import forms
from .core_logic import USER_INTERESTS

class InterestForm(forms.Form):
    interests = forms.MultipleChoiceField(
        choices=[(key, key) for key in USER_INTERESTS.keys()],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
