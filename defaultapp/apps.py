from django.apps import AppConfig


class DefaultappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'defaultapp'

    def ready(self):
        import defaultapp.signals
