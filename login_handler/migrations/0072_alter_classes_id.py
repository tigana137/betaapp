# Generated by Django 4.2.2 on 2023-08-21 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0071_rename_id_3_classes_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classes',
            name='id',
            field=models.BigIntegerField(default=1),
            preserve_default=False,
        ),
    ]
