# Generated by Django 5.1.2 on 2024-10-20 23:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Espacio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('capacidad', models.IntegerField()),
                ('descripcion', models.TextField(blank=True)),
                ('disponibilidad', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_reserva', models.DateField()),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('estado', models.CharField(choices=[('Confirmada', 'Confirmada'), ('Cancelada', 'Cancelada'), ('Pendiente', 'Pendiente')], default='Pendiente', max_length=10)),
                ('espacio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.espacio')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('Confirmacion', 'Confirmacion'), ('Recordatorio', 'Recordatorio')], max_length=20)),
                ('fecha_envio', models.DateTimeField(auto_now_add=True)),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.reserva')),
            ],
        ),
    ]
