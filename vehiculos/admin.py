from django.contrib import admin
from .models import Perfil, Vehiculo, Reserva, Ubicacion

admin.site.register(Vehiculo)
admin.site.register(Reserva)
admin.site.register(Ubicacion)
admin.site.register(Perfil)
