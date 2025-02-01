# tracker/models.py
from django.db import models
from datetime import date

PERSON_CHOICES = [
    ('sebo', "Sebo"),
    ('alomi', "Alomi"),
]

LIQUID_CHOICES = [
    ('water', 'Water'),
    ('sparkling water', 'Sparkling Water'),
    ('coffee', 'Coffee'),
    ('tea', 'Tea'),
    ('milk', 'Milk'),
    ('juice', 'Juice'),
    ('soda', 'Soda'),
    ('beer', 'Beer'),
    ('wine', 'Wine'),
    ('other', 'Other'),
]

class WaterIntake(models.Model):
    person = models.CharField(max_length=10, choices=PERSON_CHOICES, default='alomi')
    amount = models.FloatField(help_text="Amount of liquid in ounces")
    liquid_type = models.CharField(max_length=50, choices=LIQUID_CHOICES, default='water')
    entry_date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.get_person_display()} drank {self.amount} oz of {self.liquid_type} on {self.entry_date}"
