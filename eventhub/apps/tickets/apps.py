from django.apps import AppConfig


class TicketsConfig(AppConfig):
    """
    Tickets app configuration.
    ready() method imports the signals module to register signal receivers.
    """

    name = 'tickets'

    def ready(self):
        import tickets.signals      # pylint: disable=unused-import
