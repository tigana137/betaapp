# Generated by Django 4.2.2 on 2023-06-29 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0007_profs_alter_eleves_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='classes',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]