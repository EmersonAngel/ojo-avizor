# Imagen de Ojo Avizor. Pensada para desarrollo (docker-compose, con el
# código montado y `runserver`) y para producción (gunicorn + WhiteNoise,
# ver config/settings/produccion.py) desde la misma imagen — solo cambia
# el comando y las variables de entorno, no la construcción.
FROM python:3.12-slim

# libjpeg/zlib: Pillow los necesita para abrir/guardar JPEG y PNG al
# comprimir las fotos de avistamiento (RF-02). psycopg2-binary no
# requiere libpq del sistema: la trae empaquetada.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.produccion

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# collectstatic no necesita conexión a la base de datos ni un
# DJANGO_SECRET_KEY real (config/settings/base.py trae un valor de
# respaldo para este caso); sí necesita que las apps sean importables.
RUN python manage.py collectstatic --noinput

RUN useradd --create-home --uid 1000 ojo_avizor \
    && chown -R ojo_avizor:ojo_avizor /app
USER ojo_avizor

EXPOSE 8000

# Se invoca con "sh entrypoint.sh" (no "./entrypoint.sh") para no
# depender del bit de ejecución del archivo: en desarrollo, el
# docker-compose monta el código del host sobre /app y ese bit no
# siempre sobrevive un checkout en Windows.
ENTRYPOINT ["sh", "entrypoint.sh"]
# Forma shell a propósito, no la de lista/exec (ver README.md, "Despliegue
# gratuito"): Render le asigna el puerto real al contenedor por la
# variable de entorno PORT (no siempre 8000), y solo se puede leer una
# variable de entorno en el comando si Docker lo pasa por una shell. El
# despliegue con Docker/VPS no define PORT, así que cae en el 8000 de
# siempre — este mismo Dockerfile sirve para los dos despliegues sin
# cambiar nada más.
CMD gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
