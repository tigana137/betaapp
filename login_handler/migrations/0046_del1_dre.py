# Generated by Django 4.2.2 on 2023-08-15 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0045_remove_sexeeleves_id_alter_sexeeleves_nom'),
    ]

    operations = [
        migrations.CreateModel(
            name='del1',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='dre',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
    ]