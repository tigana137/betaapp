# Generated by Django 4.2.2 on 2023-08-21 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0073_eleves_id_1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eleves',
            name='eid',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='eleves',
            name='id_1',
            field=models.BigIntegerField(default=1, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
