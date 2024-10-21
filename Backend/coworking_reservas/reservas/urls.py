from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EspacioViewSet, ReservaViewSet
from . import views

router = DefaultRouter()
router.register(r'espacios', EspacioViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('espacios/', views.espacios_disponibles, name='espacios'),
    path('reservar/<int:espacio_id>/', views.reservar_espacio, name='reservar'),
    path('crear-espacio/', views.crear_espacio, name='crear_espacio'),
]
