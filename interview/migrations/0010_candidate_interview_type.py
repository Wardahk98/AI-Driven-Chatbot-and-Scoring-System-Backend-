# Generated by Django 5.2.4 on 2025-07-10 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0009_candidate_cnic'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='interview_type',
            field=models.CharField(choices=[('hr', 'HR Interview'), ('academic', 'Academic Interview')], default='hr', max_length=20),
        ),
    ]
