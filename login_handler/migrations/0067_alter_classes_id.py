# Generated by Django 4.2.2 on 2023-08-21 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0066_classes_ecole_eleves_ecole_elevestransfer_ecole_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classes',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]
