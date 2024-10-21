from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .models import Espacio, Reserva
from .serializers import EspacioSerializer, ReservaSerializer
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

class EspacioViewSet(viewsets.ModelViewSet):
    queryset = Espacio.objects.all()
    serializer_class = EspacioSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    
def index(request):
    return render(request, 'reservas/index.html')

@login_required
def crear_espacio(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        capacidad = request.POST['capacidad']
        descripcion = request.POST['descripcion']
        disponibilidad = request.POST['disponibilidad'] == 'True'

        # Crear un nuevo espacio
        Espacio.objects.create(
            nombre=nombre,
            capacidad=capacidad,
            descripcion=descripcion,
            disponibilidad=disponibilidad
        )
        messages.success(request, 'El espacio ha sido creado exitosamente.')
        return redirect('espacios')

    return render(request, 'reservas/crear_espacio.html')
    
def espacios_disponibles(request):
    espacios = Espacio.objects.filter(disponibilidad=True)
    return render(request, 'reservas/espacios.html', {'espacios': espacios})

@login_required
def reservar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, pk=espacio_id)
    if request.method == 'POST':
        fecha_reserva = request.POST['fecha_reserva']
        hora_inicio = request.POST['hora_inicio']
        hora_fin = request.POST['hora_fin']
        
        # Crear la reserva
        Reserva.objects.create(
            usuario=request.user,
            espacio=espacio,
            fecha_reserva=fecha_reserva,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado='Pendiente'
        )
        
        # Redirigir a la página de espacios
        return redirect('espacios')
    
    return render(request, 'reservas/reservar.html', {'espacio': espacio})