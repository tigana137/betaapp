# Generated by Django 4.2.2 on 2023-07-31 18:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login_handler', '0038_rename_eleves2_eleves'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eleves',
            name='class_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='students', to='login_handler.classes'),
        ),
        migrations.AlterField(
            model_name='eleves',
            name='next_class_id',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='next_students', to='login_handler.classes'),
        ),
        migrations.CreateModel(
            name='Eleves2',
            fields=[
                ('eid', models.IntegerField()),
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=40)),
                ('prenom', models.CharField(max_length=40)),
                ('sexe', models.CharField(max_length=10)),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('moyen', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('resultat', models.CharField(blank=True, max_length=25, null=True)),
                ('is_graduated', models.BooleanField(blank=True, default=None, null=True)),
                ('class_id2', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='students2', to='login_handler.classes')),
                ('next_class_id2', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='next_students2', to='login_handler.classes')),
            ],
            options={
                'ordering': ['nom', 'prenom'],
            },
        ),
    ]
