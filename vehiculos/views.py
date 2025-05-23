import stripe
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm
from .models import Perfil
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .models import Vehiculo, Reserva,Ubicacion, HistorialRenta
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required, user_passes_test
from .forms import VehiculoForm, UbicacionForm, PerfilForm
from django.contrib import messages
from django.conf import settings
from django.urls import reverse


stripe.api_key = settings.STRIPE_SECRET_KEY


def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()

            # Crear perfil asociado
            Perfil.objects.create(
                usuario=user,
                telefono=form.cleaned_data.get('telefono'),
                direccion=form.cleaned_data.get('direccion'),
                fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento')
            )

            login(request, user)
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'vehiculos/registro_informacion.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            return render(request, 'vehiculos/login.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'vehiculos/login.html')

@login_required
def inicio(request):
    return render(request, 'vehiculos/inicio.html')

@login_required
def mis_reservas(request):
    if request.user.is_superuser:
        reservas = Reserva.objects.all()
    else:
        reservas = Reserva.objects.filter(usuario=request.user)

    return render(request, 'vehiculos/mis_reservas.html', {'reservas': reservas})

@login_required
def eliminar_reserva(request, id):
    reserva = get_object_or_404(Reserva, pk=id)

    # Solo permite que el dueño de la reserva o un admin eliminen
    if not (request.user == reserva.usuario or request.user.is_staff):
        messages.error(request, "No tienes permiso para eliminar esta reserva.")
        return redirect('mis_reservas')

    # Marcar el vehículo como disponible
    vehiculo = reserva.vehiculo
    vehiculo.disponible = True
    vehiculo.save()

    # Eliminar la reserva
    reserva.delete()
    messages.success(request, "Reserva eliminada correctamente.")
    return redirect('mis_reservas')

@staff_member_required
@user_passes_test(lambda u: u.is_staff)
def añadir_vehiculo(request):
    if request.method == 'POST':
        vehiculo_form = VehiculoForm(request.POST, request.FILES)  # Maneja imágenes también

        if vehiculo_form.is_valid():
            vehiculo_form.save()
            messages.success(request, "Vehículo agregado correctamente")
            return redirect('admin_vehiculos')
        else:
            print(vehiculo_form.errors)  # Debug

    else:
        vehiculo_form = VehiculoForm()

    return render(request, 'vehiculos/añadir_vehiculo.html', {
        'vehiculo_form': vehiculo_form,
    })

@staff_member_required
def admin_vehiculos(request):
    vehiculos = Vehiculo.objects.all()

    if request.method == 'POST':
        vehiculo_id = request.POST.get('vehiculo_id')
        vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)

        if 'editar_vehiculo' in request.POST:
            vehiculo.modelo = request.POST.get(f'vehiculo_{vehiculo_id}-modelo')
            vehiculo.tipo = request.POST.get(f'vehiculo_{vehiculo_id}-tipo')
            vehiculo.placa = request.POST.get(f'vehiculo_{vehiculo_id}-placa')
            vehiculo.precio_renta = request.POST.get(f'vehiculo_{vehiculo_id}-precio_renta')
            vehiculo.precio_reserva = request.POST.get(f'vehiculo_{vehiculo_id}-precio_reserva')

            # Verifica si se cargó una imagen nueva
            if f"vehiculo_{vehiculo_id}-imagen" in request.FILES:
                vehiculo.imagen = request.FILES[f"vehiculo_{vehiculo_id}-imagen"]

            vehiculo.save()
            return redirect('admin_vehiculos')

        elif 'eliminar_vehiculo' in request.POST:
            vehiculo.delete()
            return redirect('admin_vehiculos')

    return render(request, 'vehiculos/admin_vehiculos.html', {'vehiculos': vehiculos})

@staff_member_required
def administrar_sedes(request, id_ubicacion=None):
    sedes = Ubicacion.objects.all()
    
    # Si se está editando una sede
    if id_ubicacion:
        sede_a_editar = get_object_or_404(Ubicacion, pk=id_ubicacion)
        if request.method == 'POST':
            form = UbicacionForm(request.POST, instance=sede_a_editar)
            if form.is_valid():
                form.save()
                return redirect('administrar_sedes')
        else:
            form = UbicacionForm(instance=sede_a_editar)
    else:
        # Si se está agregando una nueva sede
        sede_a_editar = None
        if request.method == 'POST':
            form = UbicacionForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('administrar_sedes')
        else:
            form = UbicacionForm()

    return render(request, 'vehiculos/admin_sedes.html', {
        'sedes': sedes,
        'form': form,
        'sede_a_editar': sede_a_editar,
    })


@staff_member_required
def eliminar_sede(request, id_ubicacion):
    sede = get_object_or_404(Ubicacion, pk=id_ubicacion)
    sede.delete()
    return redirect('administrar_sedes')

@login_required
def editar_perfil(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('editar_perfil')
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'vehiculos/editar_perfil.html', {'form': form})

@login_required
def eliminar_perfil(request, id):
    perfil = get_object_or_404(Perfil, pk=id, usuario=request.user)

    if request.method == 'POST':
        perfil.delete()
        messages.success(request, "Tu perfil ha sido eliminado.")
        return redirect('gestion_perfiles')

    messages.error(request, "Acción no permitida.")
    return redirect('gestion_perfiles')

def buscar_vehiculos(request):
    ubicaciones = Ubicacion.objects.all()
    return render(request, 'vehiculos/buscar_vehiculos.html', {
        'ubicaciones': ubicaciones
    })
def resultados_busqueda(request):
    ubicacion_id = request.GET.get('ubicacion')
    
    if not ubicacion_id:
        return redirect('buscar_vehiculos')
    
    vehiculos = Vehiculo.objects.filter(ubicacion_id=ubicacion_id)
    ubicacion_actual = Ubicacion.objects.filter(id_ubicacion=ubicacion_id).first()  # usa id_ubicacion

    return render(request, 'vehiculos/buscar_resultados.html', {
        'vehiculos': vehiculos,
        'ubicacion_actual': ubicacion_actual
    })

@login_required
def reservar_vehiculo(request, id_vehiculo):

    vehiculo = get_object_or_404(Vehiculo, pk=id_vehiculo)

    if not vehiculo.disponible:
        messages.error(request, "Este vehículo ya ha sido reservado por otro usuario.")
        return redirect('mis_reservas')

    usuario = request.user

    try:
        perfil = usuario.perfil
    except Perfil.DoesNotExist:
        messages.error(request, "Debes completar tu perfil antes de reservar.")
        return redirect('editar_perfil')

    # Validar licencia
    if not (perfil.numero_licencia and perfil.licencia_frontal and perfil.licencia_trasera and perfil.licencia_verificada):
        messages.error(request, "No puedes reservar hasta que tu licencia haya sido verificada.")
        return redirect('editar_perfil')

   
    # Crear reserva (aún sin el session_id)
    reserva = Reserva.objects.create(usuario=usuario, vehiculo=vehiculo)

    vehiculo.disponible = False
    vehiculo.save()

    # Crear sesión de Stripe
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'cop',
                'unit_amount': int(vehiculo.precio_reserva * 100),
                'product_data': {
                    'name': f"Reserva de {vehiculo.modelo} - {vehiculo.tipo}",
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/reserva/exito/{reserva.id}/'),
        cancel_url=request.build_absolute_uri(f'/reserva/cancelada/{reserva.id}/'),
    )

    # Guardar session_id en la reserva
    reserva.session_id = session.id
    reserva.save()

    return redirect(session.url, code=303)

@login_required
def reserva_exitosa(request, id):
    
    reserva = get_object_or_404(Reserva, pk=id, usuario=request.user)
    session = stripe.checkout.Session.retrieve(reserva.session_id)

    if session.payment_status == 'paid':
        reserva.pagado = True
        reserva.save()
        messages.success(request, "¡Reserva completada con éxito!")
    else:
        messages.warning(request, "El pago aún no se ha confirmado.")

    return render(request, 'vehiculos/exito.html', {'reserva': reserva})

@login_required
def reserva_cancelada(request, id):
    reserva = get_object_or_404(Reserva, pk=id, usuario=request.user)
    reserva.delete()
    messages.info(request, "Reserva cancelada.")
    return render(request, 'vehiculos/cancelada.html')

@staff_member_required
def admin_perfiles(request):
    return render(request, 'vehiculos/perfil_inicio.html')

@staff_member_required
def gestionar_perfiles(request):
    perfiles = Perfil.objects.all()
    return render(request, 'vehiculos/gestion_perfiles.html', {'perfiles': perfiles})

@staff_member_required
def verificar_licencias(request):
    perfiles = Perfil.objects.exclude(licencia_frontal=None).exclude(licencia_trasera=None)
    return render(request, 'vehiculos/verificar_licencias.html', {'perfiles': perfiles})

@staff_member_required
def verificar_licencia(request, perfil_id):
    perfil = get_object_or_404(Perfil, id_perfil=perfil_id)

    if request.method == 'POST':
        perfil.licencia_verificada = True
        perfil.save()
        return redirect('verificar_licencias')

    return render(request, 'vehiculos/detalle_licencia.html', {'perfil': perfil})

@login_required
def rentar_vehiculo(request, id):
    reserva = get_object_or_404(Reserva, pk=id, usuario=request.user)

    if reserva.pagado and not reserva.rentado:
        reserva.rentado = True
        reserva.fecha_renta = timezone.now()
        reserva.save()
        messages.success(request, "Has rentado el vehículo con éxito.")
    else:
        messages.warning(request, "No puedes rentar este vehículo.")

    return redirect('mis_reservas')

@login_required
def devolver_vehiculo(request, id):
    reserva = get_object_or_404(Reserva, pk=id, usuario=request.user)

    if reserva.rentado and not reserva.devuelto:
        # Calcular total a pagar
        reserva.fecha_devolucion = timezone.now()
        dias = reserva.calcular_dias_rentado()
        precio_por_dia = reserva.vehiculo.precio_renta
        total = dias * precio_por_dia

        reserva.total_a_pagar = total
        reserva.save()

        # Crear sesión de Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'cop',
                    'product_data': {
                        'name': f'{reserva.vehiculo.modelo}',
                    },
                    'unit_amount': int(total * 100),  # Stripe cobra en centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('pago_exitoso', args=[reserva.id])
            ),
            cancel_url=request.build_absolute_uri(
                reverse('mis_reservas')
            ),
        )

        return redirect(session.url, code=303)

    else:
        messages.warning(request, "No puedes devolver este vehículo.")
        return redirect('mis_reservas')




@login_required
def pago_exitoso(request, id):
    reserva = get_object_or_404(Reserva, pk=id, usuario=request.user)

    if not reserva.pagado:
        # Marcar como devuelto y pagado
        reserva.rentado = False
        reserva.devuelto = True
        reserva.pagado = True
        reserva.save()

        dias_rentados = reserva.calcular_dias_rentado()


        # Eliminar la reserva
        reserva.delete()

        messages.success(request, "Pago exitoso. ¡Gracias por usar nuestro servicio!")
    else:
        messages.info(request, "Este pago ya fue procesado.")

    return redirect('mis_reservas')


@staff_member_required
def historial_rentas(request):
    reservas = HistorialRenta.objects.filter(devuelto=True).order_by('-fecha_devolucion')
    return render(request, 'vehiculos/historial_rentas.html', {'reservas': reservas})


@login_required
def gestion_perfiles(request):
    perfiles = Perfil.objects.all()
    return render(request, 'vehiculos/gestion_perfiles.html', {'perfiles': perfiles})
