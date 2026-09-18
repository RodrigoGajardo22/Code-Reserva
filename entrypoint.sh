#!/bin/sh
set -e

cd /app/WebApp

echo "==> Aplicando migraciones..."
PROJECT_APPS=$(DJANGO_SETTINGS_MODULE=WebApp.settings python -c "import django; django.setup(); from django.conf import settings; print(' '.join(a for a in settings.INSTALLED_APPS if not a.startswith('django.')))")
python manage.py makemigrations --noinput $PROJECT_APPS
python manage.py migrate

echo "==> Sembrando datos de ejemplo (si no existen)..."
python manage.py seed

echo "==> Creando superusuario (admin/admin) si no existe..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
    print('Superusuario creado: admin / admin')
else:
    print('Superusuario ya existe')
"

echo "==> Levantando el servidor en http://127.0.0.1:8000/ ..."
python manage.py runserver 0.0.0.0:8000 &
SERVER_PID=$!

LOG="$(mktemp)"
echo "==> Conectando túnel Cloudflare (quick tunnel)..."
cloudflared tunnel --url http://127.0.0.1:8000 --no-autoupdate > "$LOG" 2>&1 &
CLOUDFLARED_PID=$!

URL=""
i=0
while [ -z "$URL" ] && [ "$i" -lt 60 ]; do
    i=$((i+1))
    if ! kill -0 "$CLOUDFLARED_PID" 2>/dev/null; then
        echo "Error: cloudflared no pudo arrancar:" >&2
        cat "$LOG" >&2
        exit 1
    fi
    URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | head -1)
    [ -z "$URL" ] && sleep 1
done

if [ -z "$URL" ]; then
    echo "No se obtuvo la URL a tiempo (log):" >&2
    cat "$LOG" >&2
    exit 1
fi

echo
echo "=============================================================="
echo "   Sistema en produccion. Link: $URL"
echo "=============================================================="
echo "   Admin:   $URL/admin/        (usuario: admin / admin)"
echo "   Swagger: $URL/api/docs/"
echo "=============================================================="
echo

exec tail -f "$LOG"
