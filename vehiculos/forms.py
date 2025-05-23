from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil
from .models import Vehiculo, Ubicacion

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=15, required=False)
    direccion = forms.CharField(max_length=255, required=False)
    fecha_nacimiento = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'telefono', 'direccion', 'fecha_nacimiento']

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['modelo', 'tipo', 'placa','precio_reserva','precio_renta', 'imagen', 'ubicacion', 'activo', 'disponible']  # ← Campo añadido
        widgets = {
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_reserva': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_renta': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.URLInput(attrs={'class': 'form-control'}),  # ← Campo añadido
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['nombre', 'ciudad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la sede'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
        }

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['telefono', 'direccion', 'fecha_nacimiento', 'foto', 'numero_licencia', 'licencia_frontal', 'licencia_trasera']
        exclude = ['usuario']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'  # opcional si usas Bootstrap
            }),
        }