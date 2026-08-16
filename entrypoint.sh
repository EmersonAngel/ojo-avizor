#!/bin/sh
# Punto de entrada del contenedor: espera a que Postgres acepte conexiones
# (el contenedor de la app puede arrancar antes de que la base de datos
# termine de inicializar), aplica migraciones y solo entonces ejecuta el
# comando real (gunicorn en producción, runserver en desarrollo).
set -e

host="${DB_HOST:-localhost}"
port="${DB_PORT:-5432}"

echo "Esperando la base de datos en $host:$port..."
until python -c "
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
sys.exit(0 if s.connect_ex(('$host', $port)) == 0 else 1)
"; do
    sleep 1
done
echo "Base de datos disponible."

python manage.py migrate --noinput

exec "$@"
