# Generated by Django 4.2.2 on 2023-08-19 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0064_elevestransfer_level_elevestransfer_sexe'),
    ]

    operations = [
        migrations.AddField(
            model_name='elevestransfer',
            name='is_graduated',
            field=models.BooleanField(blank=True, max_length=10, null=True),
        ),
    ]
