# Generated by Django 3.1 on 2021-02-19 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_assignment_mandatory_functions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='mandatory_functions',
        ),
        migrations.AddField(
            model_name='task',
            name='mandatory_functions',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
