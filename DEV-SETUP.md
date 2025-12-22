# Eventhub - Getting Started 🛠️

This document is for **developer reference**.

## Clone the repository

```bash
git clone https://github.com/marythedev/eventhub.git
cd eventhub
```

## Install Requirements

```bash
pip install -r requirements.txt
```

## Setup Environmental Variables
Rename `.env.template` file to `.env` and update variables with appropriate values.

Secret Key Generation
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Disable Security Settings
Disable security headers in `settings.py` since they block the app on `localhost (http)`.

```bash
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'http')
```

> **❗️For production, these headers must be enabled.**

## Start the App
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

> Go to: `http://localhost:8000/`
