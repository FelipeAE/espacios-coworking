# Generated by Django 5.0.1 on 2024-11-20 02:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0002_notificacion_leida'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='reserva',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificacion', to='reservas.reserva'),
        ),
    ]
