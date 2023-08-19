# Generated by Django 4.2.2 on 2023-06-25 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0006_alter_eleves_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='profs',
            fields=[
                ('eid', models.IntegerField(primary_key=True, serialize=False)),
                ('id', models.BigIntegerField(blank=True, default=0, null=True)),
                ('nom', models.CharField(max_length=40)),
                ('prenom', models.CharField(max_length=40)),
            ],
        ),
        migrations.AlterField(
            model_name='eleves',
            name='id',
            field=models.BigIntegerField(blank=True, default=0, null=True),
        ),
    ]
