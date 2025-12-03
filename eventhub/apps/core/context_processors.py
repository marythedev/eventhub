from django.conf import settings


def file_upload_settings(request):
    """File upload related settings for templates."""
    return {
        'MAX_UPLOAD_MB': settings.MAX_UPLOAD_MB
    }

def fee_settings(request):
    """Fees related settings for templates."""
    return {
        'SERVICE_FEE': settings.SERVICE_FEE,
        'TAX': settings.TAX
    }
