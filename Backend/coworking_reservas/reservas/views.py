from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .models import Espacio, Reserva
from .serializers import EspacioSerializer, ReservaSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm


class EspacioViewSet(viewsets.ModelViewSet):
    queryset = Espacio.objects.all()
    serializer_class = EspacioSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    
def index(request):
    return render(request, 'reservas/index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'reservas/register.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
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

        # Actualizar la disponibilidad del espacio
        espacio.disponibilidad = False
        espacio.save()
        
        # Mostrar un mensaje de éxito
        messages.success(request, 'Reserva realizada exitosamente y el espacio ahora está marcado como no disponible.')

        # Redirigir a la página de espacios
        return redirect('espacios')
    
    return render(request, 'reservas/reservar.html', {'espacio': espacio})

@login_required
def editar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, pk=espacio_id)
    if request.method == 'POST':
        espacio.nombre = request.POST['nombre']
        espacio.capacidad = request.POST['capacidad']
        espacio.descripcion = request.POST['descripcion']
        espacio.disponibilidad = request.POST['disponibilidad'] == 'True'
        espacio.save()

        messages.success(request, 'Espacio actualizado exitosamente.')
        return redirect('espacios')

    return render(request, 'reservas/editar_espacio.html', {'espacio': espacio})

@login_required
def eliminar_espacio(request, espacio_id):
    espacio = get_object_or_404(Espacio, pk=espacio_id)
    if request.method == 'POST':
        espacio.delete()
        messages.success(request, 'Espacio eliminado exitosamente.')
        return redirect('espacios')

    return render(request, 'reservas/eliminar_espacio.html', {'espacio': espacio})

@login_required
def ver_reservas(request):
    reservas = Reserva.objects.all() if request.user.is_staff else Reserva.objects.filter(usuario=request.user)
    return render(request, 'reservas/ver_reservas.html', {'reservas': reservas})



@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    
    if request.method == 'POST':
        # Guardar los valores enviados
        reserva.fecha_reserva = request.POST['fecha_reserva']
        reserva.hora_inicio = request.POST['hora_inicio']
        reserva.hora_fin = request.POST['hora_fin']
        
        # Si se cambia el estado a Cancelada, actualizamos la disponibilidad del espacio
        nuevo_estado = request.POST['estado']
        if nuevo_estado == "Cancelada" and reserva.estado != "Cancelada":
            reserva.espacio.disponibilidad = True
            reserva.espacio.save()
            
        # Si se cambia el estado a Confirmada, actualizamos la disponibilidad del espacio
        if nuevo_estado == "Confirmada" and reserva.estado != "Confirmada":
            reserva.espacio.disponibilidad = False
            reserva.espacio.save()
        
        reserva.estado = nuevo_estado
        reserva.save()  # Guardar los cambios
        return redirect('ver_reservas')  # Redirigir a la lista de reservas

    return render(request, 'reservas/editar_reserva.html', {'reserva': reserva})


@login_required
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    if request.method == 'POST':
        espacio = reserva.espacio
        reserva.delete()
        # Actualizar la disponibilidad del espacio asociado
        espacio.disponibilidad = True
        espacio.save()
        messages.success(request, 'Reserva eliminada exitosamente y el espacio ahora está disponible.')
        return redirect('ver_reservas')

    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})
