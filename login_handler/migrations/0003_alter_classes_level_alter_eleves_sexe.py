# Generated by Django 4.2.2 on 2023-06-24 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0002_classes_eleves'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classes',
            name='level',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='eleves',
            name='sexe',
            field=models.CharField(max_length=10),
        ),
    ]
