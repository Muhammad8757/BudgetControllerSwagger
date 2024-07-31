# Generated by Django 5.0.7 on 2024-07-31 06:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget_controller_app', '0009_alter_category_created_category_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='created_category_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_transactions', to=settings.AUTH_USER_MODEL),
        ),
    ]
