# Generated by Django 5.0.6 on 2024-07-06 09:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget_controller_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertransaction',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='budget_controller_app.category'),
        ),
        migrations.AlterField(
            model_name='usertransaction',
            name='description',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
