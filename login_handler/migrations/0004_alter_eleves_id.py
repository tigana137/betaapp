# Generated by Django 4.2.2 on 2023-06-24 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0003_alter_classes_level_alter_eleves_sexe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eleves',
            name='id',
            field=models.BigIntegerField(blank=True),
        ),
    ]