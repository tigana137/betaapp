# Generated by Django 4.2.2 on 2023-07-23 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0019_eleves_next_class_id_alter_eleves_class_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='eleves',
            name='date_naissance',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Matieres2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=80)),
                ('saisie_classe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login_handler.classes')),
                ('saisie_prof', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login_handler.profs')),
            ],
            options={
                'ordering': ['saisie_classe'],
                'unique_together': {('field', 'saisie_classe')},
            },
        ),
    ]
