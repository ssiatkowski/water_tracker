# tracker/forms.py
from django import forms
from .models import WaterIntake

class WaterIntakeForm(forms.ModelForm):
    class Meta:
        model = WaterIntake
        fields = ['person', 'amount', 'liquid_type', 'entry_date']
        widgets = {
            'person': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ounces',
                'value': 8  # default value in the widget
            }),
            'liquid_type': forms.Select(attrs={'class': 'form-control'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        # You can also set an initial value for the amount field:
        initial = {
            'amount': 8,
        }
