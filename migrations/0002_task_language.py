# Generated by Django 3.1 on 2021-03-04 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='language',
            field=models.CharField(choices=[('python3', 'Python3'), ('cpp', 'C++'), ('c', 'C'), ('matlab', 'MATLAB')], default='', max_length=20),
            preserve_default=False,
        ),
    ]