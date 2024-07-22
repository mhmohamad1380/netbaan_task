from django.apps import AppConfig


class BookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'book'

    def ready(self) -> None:
        import book.signals
        return super().ready()
