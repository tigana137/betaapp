# Generated by Django 4.2.2 on 2023-08-26 03:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0110_alter_ecole_data_virgin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ecole_data',
            name='virgin',
        ),
    ]
