from django.forms import ModelForm

from .models import Cam


class CamForm(ModelForm):
    class Meta:
        model = Cam
        fields = ['name', 'max_pics', 'max_gb', 'max_days']

