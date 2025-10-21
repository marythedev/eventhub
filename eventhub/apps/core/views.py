import os
import json
from django.shortcuts import render
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()


def home(request):
    return render(request, 'core/home.html')

def explore(request):
    file_path = os.path.join(settings.APP_ROOT,'apps', 'core', 'data', 'dummy_data.json')
    with open(file_path, "r") as f:
        dummy_data = json.load(f)
    return render(request, 'core/events.html', {'events': dummy_data, 'CDN_DOMAIN': os.getenv('CDN_DOMAIN')})