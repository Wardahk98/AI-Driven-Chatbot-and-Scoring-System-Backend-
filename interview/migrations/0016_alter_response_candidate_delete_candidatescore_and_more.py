# Generated by Django 5.2.4 on 2025-07-12 10:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidate', '0001_initial'),
        ('interview', '0015_alter_candidate_invite_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='response',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candidate.candidate'),
        ),
        migrations.DeleteModel(
            name='CandidateScore',
        ),
        migrations.DeleteModel(
            name='Candidate',
        ),
    ]
