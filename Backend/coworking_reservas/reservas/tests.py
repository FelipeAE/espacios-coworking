from django.test import TestCase
from .models import Espacio

class EspacioTestCase(TestCase):
    def setUp(self):
        Espacio.objects.create(nombre="Sala de Reuniones", capacidad=15)

    def test_espacio_creado_correctamente(self):
        espacio = Espacio.objects.get(nombre="Sala de Reuniones")
        self.assertEqual(espacio.capacidad, 15)
