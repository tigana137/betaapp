# Generated by Django 4.2.2 on 2023-08-24 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0107_alter_elevestransfer_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecole_data',
            name='nbr_elev',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]