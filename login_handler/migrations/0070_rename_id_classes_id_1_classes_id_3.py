# Generated by Django 4.2.2 on 2023-08-21 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0069_remove_classes_id_1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classes',
            old_name='id',
            new_name='id_1',
        ),
        migrations.AddField(
            model_name='classes',
            name='id_3',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
