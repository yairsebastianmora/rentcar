from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('registro/', views.registro_view, name='registro'),
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('buscar/', views.buscar_vehiculos, name='buscar_vehiculos'),
    path('resultados/', views.resultados_busqueda, name='resultados_busqueda'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('reservas/', views.mis_reservas, name='mis_reservas'),
    path('reserva/eliminar/<int:id>/', views.eliminar_reserva, name='eliminar_reserva'),
    path('admin_vehiculos/', views.admin_vehiculos, name='admin_vehiculos'),
    path('admin_vehiculos/añadir/', views.añadir_vehiculo, name='añadir_vehiculo'),
    path('admin_vehiculos/', views.admin_vehiculos, name='admin_vehiculos'),
    path('admin_sedes/', views.administrar_sedes, name='administrar_sedes'),
    path('admin_sedes/<int:id_ubicacion>/', views.administrar_sedes, name='editar_sede'),
    path('eliminar_sede/<int:id_ubicacion>/', views.eliminar_sede, name='eliminar_sede'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('eliminar_perfil/<int:id_perfil>/', views.eliminar_perfil, name='eliminar_perfil'),
    path('reservar/<int:id_vehiculo>/', views.reservar_vehiculo, name='reservar_vehiculo'),
    path('reserva/exito/<int:id>/', views.reserva_exitosa, name='reserva_exitosa'),
    path('reserva/cancelada/<int:id>/', views.reserva_cancelada, name='reserva_cancelada'),
    path('perfiles', views.admin_perfiles, name='admin_perfiles'),
    path('gestion/', views.gestionar_perfiles, name='gestion_perfiles'),
    path('licencias/', views.verificar_licencias, name='verificar_licencias'),
    path('perfiles/verificar/<int:perfil_id>/', views.verificar_licencia, name='verificar_licencia'),
    path('rentar/<int:id>/', views.rentar_vehiculo, name='rentar_vehiculo'),
    path('devolver/<int:id>/', views.devolver_vehiculo, name='devolver_vehiculo'),
    path('pago-exitoso/<int:id>/', views.pago_exitoso, name='pago_exitoso'),
    path('historial/rentados/', views.historial_rentas, name='historial_rentas'),
   

]
