# Generated by Django 4.2.2 on 2023-08-22 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0082_rename_profs_profs2'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profs2',
            old_name='ecole',
            new_name='ecole2',
        ),
    ]