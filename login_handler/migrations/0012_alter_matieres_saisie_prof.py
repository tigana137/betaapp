# Generated by Django 4.2.2 on 2023-07-02 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0011_alter_classes_name_alter_matieres_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matieres',
            name='saisie_prof',
            field=models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.CASCADE, to='login_handler.profs'),
        ),
    ]
