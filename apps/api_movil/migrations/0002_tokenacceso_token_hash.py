"""Guarda el hash del token en vez del token en claro (revisión de seguridad
del 25/08/2026). La migración de datos convierte los tokens existentes a su
hash antes de quitar la columna vieja, así que ninguna sesión móvil activa
se cierra de golpe."""
import hashlib

from django.db import migrations, models


def _hash_token(token_en_claro):
    return hashlib.sha256(token_en_claro.encode()).hexdigest()


def convertir_a_hash(apps, schema_editor):
    TokenAcceso = apps.get_model('api_movil', 'TokenAcceso')
    for token in TokenAcceso.objects.all():
        token.token_hash = _hash_token(token.token)
        token.save(update_fields=['token_hash'])


def revertir_hash(apps, schema_editor):
    # No hay forma de recuperar el token en claro a partir de su hash — la
    # migración inversa deja la columna vacía en vez de fallar.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api_movil', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokenacceso',
            name='token_hash',
            field=models.CharField(default='', editable=False, max_length=64),
            preserve_default=False,
        ),
        migrations.RunPython(convertir_a_hash, revertir_hash),
        migrations.RemoveField(
            model_name='tokenacceso',
            name='token',
        ),
        migrations.AlterField(
            model_name='tokenacceso',
            name='token_hash',
            field=models.CharField(editable=False, max_length=64, unique=True),
        ),
    ]
