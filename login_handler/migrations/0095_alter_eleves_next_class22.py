# Generated by Django 4.2.2 on 2023-08-22 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0094_rename_classe_eleves_classe22_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eleves',
            name='next_class22',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='next_class22', to='login_handler.classes'),
        ),
    ]
