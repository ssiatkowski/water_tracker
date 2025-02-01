# Generated by Django 5.1.5 on 2025-02-01 20:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="waterintake",
            name="timestamp",
        ),
        migrations.AddField(
            model_name="waterintake",
            name="entry_date",
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name="waterintake",
            name="liquid_type",
            field=models.CharField(default="water", max_length=50),
        ),
        migrations.AddField(
            model_name="waterintake",
            name="person",
            field=models.CharField(
                choices=[("sebo", "Sebo"), ("alomi", "Alomi")],
                default="sebo",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="waterintake",
            name="amount",
            field=models.FloatField(help_text="Amount of liquid in ounces"),
        ),
    ]
