# Generated by Django 4.2.2 on 2023-08-22 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0088_rename_pk_profs_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classes',
            old_name='id',
            new_name='cid',
        ),
    ]
