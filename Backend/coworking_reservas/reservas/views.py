from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .models import Espacio, Reserva, Notificacion
from .serializers import EspacioSerializer, ReservaSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .forms import EditarPerfilForm


class EspacioViewSet(viewsets.ModelViewSet):
    queryset = Espacio.objects.all()
    serializer_class = EspacioSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    
def index(request):
    if request.user.is_authenticated:
        notificaciones_no_leidas = request.user.reserva_set.filter(notificacion__leida=False).count()
    else:
        notificaciones_no_leidas = 0

    return render(request, 'reservas/index.html', {
        'notificaciones_no_leidas': notificaciones_no_leidas,
    })


@login_required
def perfil_usuario(request):
    return render(request, 'reservas/perfil.html', {'usuario': request.user})

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado con éxito.')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = EditarPerfilForm(instance=request.user)
    
    return render(request, 'reservas/editar_perfil.html', {'form': form})

@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Importante para mantener la sesión del usuario
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'reservas/cambiar_contrasena.html', {'form': form})

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
            
            # Crear una notificación para el usuario que hizo la reserva
            Notificacion.objects.create(
                reserva=reserva,
                tipo='Cancelacion',
                leida=False
            )
            
        # Si se cambia el estado a Confirmada, actualizamos la disponibilidad del espacio
        if nuevo_estado == "Confirmada" and reserva.estado != "Confirmada":
            reserva.espacio.disponibilidad = False
            reserva.espacio.save()
            
            # Crear una notificación para el usuario que hizo la reserva
            Notificacion.objects.create(
                reserva=reserva,
                tipo='Confirmacion',
                leida=False
            )

        # Guardar el nuevo estado de la reserva
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

@login_required
def ver_notificaciones(request):
    if request.user.is_authenticated:
        # Obtener todas las notificaciones del usuario
        notificaciones = Notificacion.objects.filter(reserva__usuario=request.user)
    else:
        notificaciones = []

    return render(request, 'reservas/notificaciones.html', {'notificaciones': notificaciones})

@login_required
def aprobar_reserva(request, reserva_id):
    if request.user.is_staff:
        reserva = get_object_or_404(Reserva, pk=reserva_id)
        reserva.estado = 'Confirmada'
        reserva.save()

        # Crear una notificación
        Notificacion.objects.create(
            reserva=reserva,
            tipo='Confirmacion'
        )
        
        return redirect('ver_reservas')
    
@login_required
def marcar_notificacion_como_leida(request):
    if request.method == 'POST':
        notificacion_id = request.POST.get('notificacion_id')
        if notificacion_id:
            notificacion = get_object_or_404(Notificacion, pk=notificacion_id)
            # Verificar que la notificación pertenezca al usuario autenticado
            if notificacion.reserva.usuario == request.user:
                notificacion.leida = True
                notificacion.save()
    return redirect('notificaciones')