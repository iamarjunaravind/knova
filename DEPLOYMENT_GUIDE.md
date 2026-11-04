# KNOVA 2027 - Final Deployment Handover Guide

This document serves as the final technical handover for the DevOps and Staging teams responsible for bringing KNOVA 2027 to a live production environment.

## 1. Environment Variables Required
Before starting the application in a live environment, the following environment variables **must** be injected into the system (e.g., via a `.env` file or Docker secrets):

```ini
DEBUG=False
SECRET_KEY="your-secure-randomly-generated-secret-key"
DJANGO_ALLOWED_HOSTS="knova.com www.knova.com staging.knova.com"
```

*Note: If `DEBUG=False` is detected, Django will automatically enforce strict HTTPS security headers (HSTS, Secure Cookies).*

## 2. Infrastructure Requirements
The application relies on the following infrastructure components:

1. **Python 3.9+**: The core Django runtime.
2. **PostgreSQL**: Required for robust data scaling. The default SQLite database is only intended for local development.
3. **Redis**: Required as the message broker for Celery.
4. **Celery Worker**: Required to handle heavy background tasks (CSV bulk imports, email notifications, report generation).

## 3. Server Configuration (Gunicorn + NGINX)

### A. Gunicorn Supervisor Configuration
```ini
[program:knova_web]
command=/path/to/venv/bin/gunicorn knova_backend.wsgi:application --workers 4 --bind unix:/run/knova.sock
autostart=true
autorestart=true
```

### B. Celery Supervisor Configuration
```ini
[program:knova_celery]
command=/path/to/venv/bin/celery -A knova_backend worker -l info
autostart=true
autorestart=true
```

### C. NGINX Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name knova.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/project27k;
    }
    
    location /media/ {
        root /path/to/project27k;
        # Crucial Security: Prevent script execution in uploads
        location ~ \.(php|py|sh|pl|cgi)$ {
            deny all;
        }
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/run/knova.sock;
    }
}
```

## 4. Final Sanity Checks Before Launch
1. **Migrations**: Ensure you run `python manage.py migrate` on the new PostgreSQL database.
2. **Static Files**: Run `python manage.py collectstatic --noinput` to gather all CSS/JS for NGINX.
3. **Superuser**: Run `python manage.py createsuperuser` to establish the initial admin account.
4. **Deployment Check**: Run `python manage.py check --deploy` one final time on the live server to ensure no environment variables were missed.

**Congratulations on the successful build of KNOVA 2027!**
