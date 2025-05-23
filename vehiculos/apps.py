from django.apps import AppConfig


class VehiculosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vehiculos'

class MiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vehiculos'  # Reemplaa por el nombre de tu app

    def ready(self):
        import vehiculos.signals  # Asegúrate de reemplazar con el nombre real