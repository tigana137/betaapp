# Generated by Django 4.2.2 on 2023-08-15 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0050_ecole_data_stat_school_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ecole_data',
            name='del1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login_handler.del1'),
        ),
        migrations.AlterField(
            model_name='ecole_data',
            name='dre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login_handler.dre'),
        ),
    ]
