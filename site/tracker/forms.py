from django.forms import ModelForm
from tracker.models import Expenditure

class ExpenditureForm(ModelForm):
    """
    Form to input an expenditure.
    """
    class Meta(object):
        model = Expenditure
