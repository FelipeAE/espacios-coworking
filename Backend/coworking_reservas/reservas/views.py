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
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import mercadopago
import os
from dotenv import load_dotenv
import json
from django.db import models

load_dotenv()


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
        precio = request.POST['precio']

        # Crear un nuevo espacio
        Espacio.objects.create(
            nombre=nombre,
            capacidad=capacidad,
            descripcion=descripcion,
            disponibilidad=disponibilidad,
            precio=precio
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
        try:
            # Crear la reserva con estado 'Pendiente'
            reserva = Reserva.objects.create(
                usuario=request.user,
                espacio=espacio,
                fecha_reserva=request.POST['fecha_reserva'],
                hora_inicio=request.POST['hora_inicio'],
                hora_fin=request.POST['hora_fin'],
                estado='Pendiente'
            )
            
            # Inicializar el SDK de MercadoPago
            sdk = mercadopago.SDK('APP_USR-7241975703348439-103011-e9b1df29ec7ddf120c6957f8f4325b00-2068456564')
            
            # Construir URLs absolutas
            base_url = request.build_absolute_uri('/')[:-1]
            
            # Crear la preferencia para el pago
            preference_data = {
                "items": [
                    {
                        "title": f"Reserva de {espacio.nombre}",
                        "quantity": 1,
                        "currency_id": "CLP",
                        "unit_price": float(espacio.precio),  # Asumiendo que hay un precio en el modelo Espacio
                        "description": f"Reserva para el espacio {espacio.nombre} desde {reserva.hora_inicio} hasta {reserva.hora_fin}",
                    }
                ],
                "back_urls": {
                    "success": f"{base_url}{reverse('payment_success', args=[reserva.id])}",
                    "failure": f"{base_url}{reverse('payment_failure', args=[reserva.id])}",
                    "pending": f"{base_url}{reverse('payment_pending', args=[reserva.id])}"
                },
                "auto_return": "approved",
                "external_reference": str(reserva.id),
                "notification_url": f"c59c-2803-c600-9104-d807-b551-7879-1a23-41a0.ngrok-free.app/webhook",  # Ajustar la URL si es necesario.
            }
            
            # Crear la preferencia en MercadoPago
            preference_response = sdk.preference().create(preference_data)
            
            # Verificar si la respuesta es exitosa
            if preference_response["status"] in [200, 201]:
                # Obtener la URL de pago
                init_point = preference_response["response"]["init_point"]
                
                # En modo desarrollo, usar sandbox_init_point
                if os.getenv('DEBUG', 'False').lower() == 'true':
                    init_point = preference_response["response"]["sandbox_init_point"]
                
                # Redirigir directamente a la página de pago de MercadoPago
                return redirect(init_point)
            else:
                error_detail = json.dumps(preference_response, indent=2)
                messages.error(request, f"Error al crear la preferencia de pago. Detalles: {error_detail}")
                return redirect('espacios')

        except Exception as e:
            import traceback
            print(f"Error completo: {str(e)}")
            print(traceback.format_exc())
            
            # Si hay un error, eliminar la reserva si fue creada
            if 'reserva' in locals():
                try:
                    reserva.delete()
                except:
                    pass
            
            messages.error(request, f"Hubo un problema al procesar tu reserva. Inténtalo de nuevo más tarde.")
            return redirect('espacios')
    
    return render(request, 'reservas/reservar.html', {'espacio': espacio})

# Vistas para manejar el resultado del pago
def payment_success(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    
    # Actualizar la reserva a pagada
    reserva.payment_id = payment_id
    reserva.estado = 'Confirmada'
    reserva.save()
    
    return render(request, 'reservas/payment_success.html', {
        'reserva': reserva,
        'payment_id': payment_id,
        'status': status
    })

def payment_failure(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    error = request.GET.get('error')
    
    # Actualizar el estado de la reserva a fallida
    reserva.estado = 'Fallida'
    reserva.save()
    
    return render(request, 'reservas/payment_failure.html', {
        'reserva': reserva,
        'error': error
    })

def payment_pending(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Actualizar el estado de la reserva a pendiente
    reserva.estado = 'Pendiente'
    reserva.save()
    
    return render(request, 'reservas/payment_pending.html', {
        'reserva': reserva
    })

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if data["type"] == "payment":
                payment_id = data["data"]["id"]
                
                # Inicializar SDK
                sdk = mercadopago.SDK('APP_USR-7241975703348439-103011-e9b1df29ec7ddf120c6957f8f4325b00-2068456564')
                
                # Obtener información del pago
                payment_info = sdk.payment().get(payment_id)
                
                if payment_info["status"] == 200:
                    payment = payment_info["response"]
                    external_reference = payment.get("external_reference")
                    
                    if external_reference:
                        try:
                            reserva = Reserva.objects.get(id=external_reference)
                            reserva.payment_id = payment_id
                            reserva.estado = payment["status"]
                            reserva.save()
                        except Reserva.DoesNotExist:
                            return HttpResponse(status=404)
                
                return HttpResponse(status=200)
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return HttpResponse(status=400)
    
    return HttpResponse(status=200)

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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Reserva, Espacio

@login_required
@user_passes_test(lambda u: u.is_staff)  # Solo los administradores pueden ver el dashboard
def dashboard(request):
    # Total de reservas
    total_reservas = Reserva.objects.count()

    # Reservas confirmadas
    reservas_confirmadas = Reserva.objects.filter(estado='Confirmada').count()

    # Reservas canceladas
    reservas_canceladas = Reserva.objects.filter(estado='Cancelada').count()

    # Espacios más reservados
    espacios_populares = (
        Espacio.objects
        .annotate(num_reservas=models.Count('reserva'))
        .order_by('-num_reservas')[:5]
    )

    # Datos para un gráfico (por ejemplo, número de reservas por mes)
    reservas_por_mes = (
        Reserva.objects
        .extra(select={'month': "EXTRACT(month FROM fecha_reserva)"})
        .values('month')
        .annotate(total=models.Count('id'))
        .order_by('month')
    )

    context = {
        'total_reservas': total_reservas,
        'reservas_confirmadas': reservas_confirmadas,
        'reservas_canceladas': reservas_canceladas,
        'espacios_populares': espacios_populares,
        'reservas_por_mes': reservas_por_mes,
    }
    
    return render(request, 'reservas/dashboard.html', context)
