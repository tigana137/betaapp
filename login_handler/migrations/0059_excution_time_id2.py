# Generated by Django 4.2.2 on 2023-08-18 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0058_rename_text_excution_time_funct_excution_time_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='excution_time',
            name='id2',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
