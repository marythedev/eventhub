from django.shortcuts import render

# TODO: home page for logged in user
def home(request):
    return render(request, 'core/home.html')
