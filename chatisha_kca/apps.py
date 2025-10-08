from django.apps import AppConfig


class ChatishaKcaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatisha_kca'

    def ready(self):
        import chatisha_kca.signals