from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from rest_framework.routers import DefaultRouter
from .views import EspacioViewSet, ReservaViewSet
from . import views

router = DefaultRouter()
router.register(r'espacios', EspacioViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='reservas/login.html', redirect_authenticated_user=True, next_page='index'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path(
        'perfil/cambiar_contrasena/', 
        PasswordChangeView.as_view(
            template_name='reservas/cambiar_contrasena.html',
            success_url=reverse_lazy('perfil_usuario')
        ), 
        name='cambiar_contrasena'
    ),
    path('espacios/', views.espacios_disponibles, name='espacios'),
    path('reservar/<int:espacio_id>/', views.reservar_espacio, name='reservar'),
    path('pago/exito/<int:reserva_id>/', views.payment_success, name='payment_success'),
    path('pago/fallo/<int:reserva_id>/', views.payment_failure, name='payment_failure'),
    path('pago/pendiente/<int:reserva_id>/', views.payment_pending, name='payment_pending'),
    path('webhook/', views.webhook, name='webhook'),
    path('crear-espacio/', views.crear_espacio, name='crear_espacio'),
    path('editar-espacio/<int:espacio_id>/', views.editar_espacio, name='editar_espacio'),
    path('eliminar-espacio/<int:espacio_id>/', views.eliminar_espacio, name='eliminar_espacio'),
    path('ver-reservas/', views.ver_reservas, name='ver_reservas'),
    path('editar-reserva/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('eliminar-reserva/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('notificaciones/', views.ver_notificaciones, name='notificaciones'),
    path('notificaciones/marcar/', views.marcar_notificacion_como_leida, name='marcar_notificacion_como_leida'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
