from django import forms
from .services.newsdata_service import get_interest_choices

class InterestForm(forms.Form):
    interests = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interests"].choices = get_interest_choices()
