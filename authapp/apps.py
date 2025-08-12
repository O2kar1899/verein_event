from django.apps import AppConfig

class AuthConfig(AppConfig):  # Klasse muss 'AuthConfig' heißen
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authapp'  # Muss exakt dem Ordnernamen entsprechen (kleingeschrieben)