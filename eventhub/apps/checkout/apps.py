from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    """
    Checkout app configuration.
    ready() method imports the signals module to register signal receivers.
    """

    name = 'checkout'

    def ready(self):
        import checkout.signals  # pylint: disable=unused-import
