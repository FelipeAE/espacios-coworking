from django.urls import path, include
from django.contrib.auth import views as auth_views
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
    path('espacios/', views.espacios_disponibles, name='espacios'),
    path('reservar/<int:espacio_id>/', views.reservar_espacio, name='reservar'),
    path('crear-espacio/', views.crear_espacio, name='crear_espacio'),
    path('editar-espacio/<int:espacio_id>/', views.editar_espacio, name='editar_espacio'),
    path('eliminar-espacio/<int:espacio_id>/', views.eliminar_espacio, name='eliminar_espacio'),
    path('ver-reservas/', views.ver_reservas, name='ver_reservas'),
    path('editar-reserva/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('eliminar-reserva/<int:reserva_id>/', views.eliminar_reserva, name='eliminar_reserva'),
]
