from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

class Perfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    numero_licencia = models.CharField(max_length=30, blank=True, null=True)
    licencia_frontal = models.ImageField(upload_to='licencias/frontal/', blank=True, null=True)
    licencia_trasera = models.ImageField(upload_to='licencias/trasera/', blank=True, null=True)
    licencia_verificada = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.username

class Ubicacion(models.Model):
    id_ubicacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"

class Vehiculo(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    modelo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)  # SUV, Sedan, etc.
    placa = models.CharField(max_length=20)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    imagen = models.URLField()
    activo = models.BooleanField(default=True)
    disponible = models.BooleanField(default=True)
    precio_reserva = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # antes llamado precio_actual
    precio_renta = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)    # nuevo campo agregado

    def __str__(self):
        return f'{self.modelo} - {self.placa}'



class Reserva(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    fecha_renta = models.DateTimeField(null=True, blank=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    pagado = models.BooleanField(default=False)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    rentado = models.BooleanField(default=False)
    devuelto = models.BooleanField(default=False)
    total_a_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def calcular_dias_rentado(self):
        if self.fecha_renta and self.fecha_devolucion:
            return max((self.fecha_devolucion - self.fecha_renta).days, 1)
        return 0

    def __str__(self):
        return f"Reserva de {self.vehiculo} por {self.usuario}"
    

class HistorialRenta(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_reserva = models.DateTimeField()
    fecha_renta = models.DateTimeField()
    fecha_devolucion = models.DateTimeField()
    dias_rentados = models.IntegerField()
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.vehiculo} rentado por {self.usuario}"