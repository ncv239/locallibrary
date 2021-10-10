from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class RenewBookForm(forms.Form):
    """Form for a librarian to renew books"""
    
    # we use widget to pop up datepicker
    renewal_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),
        help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):

        # use default sanitized of potentially unsafe input using the default validators,
        # and converted into the correct standard type for the data
        data = self.cleaned_data["renewal_date"]

        #check if a date is not in the past
        if data < datetime.date.today():
            raise ValidationError(_("Invalid date - renewal in past"))
        
        # Check if a date is in the allowed range (+4 weeks from today)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_("Invalid date - renewal more than 4 weeks ahead"))
        
        # Return the cleaned data
        return data
