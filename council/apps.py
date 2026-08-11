from django.apps import AppConfig


class CouncilConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "council"
    verbose_name = "Совет прихода"

    def ready(self):
        from . import signals  # noqa: F401
