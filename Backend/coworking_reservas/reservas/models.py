from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Espacio(models.Model):
    nombre = models.CharField(max_length=100)
    capacidad = models.IntegerField()
    descripcion = models.TextField(blank=True)
    disponibilidad = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    ESTADOS = [
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
        ('Pendiente', 'Pendiente'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')

    def __str__(self):
        return f'Reserva de {self.usuario} en {self.espacio} el {self.fecha_reserva}'

class Notificacion(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[('Confirmacion', 'Confirmacion'), ('Recordatorio', 'Recordatorio')])
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notificación {self.tipo} para {self.reserva}'
