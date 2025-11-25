from django.shortcuts import render


# TODO: home page for logged in user
def home(request):
    """User's home page."""
    return render(request, 'core/home.html')
