# Generated by Django 4.2.2 on 2023-08-26 21:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0112_ecole_data_virgin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classes',
            name='count',
        ),
        migrations.RemoveField(
            model_name='classes',
            name='female_count',
        ),
        migrations.RemoveField(
            model_name='classes',
            name='male_count',
        ),
        migrations.RemoveField(
            model_name='classes',
            name='next_class_id',
        ),
    ]
