# Generated by Django 4.2.2 on 2023-08-15 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0044_sexeeleves'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sexeeleves',
            name='id',
        ),
        migrations.AlterField(
            model_name='sexeeleves',
            name='nom',
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
    ]
