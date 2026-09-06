from django.db import migrations, models


def asignar_codigos_legacy(apps, schema_editor):
    # Genera códigos deterministas para productos creados antes de existir este campo,
    # evitando colisiones antes de activar la restricción unique.
    producto_model = apps.get_model('inventario', 'Producto')
    for producto in producto_model.objects.all():
        producto.codigo = f'LEGACY-{producto.pk:06d}'
        producto.save(update_fields=['codigo'])


class Migration(migrations.Migration):
    # Añade código en tres pasos para mantener compatibles las bases con datos existentes.
    dependencies = [
        ('inventario', '0002_cliente_venta_detalleventa'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='codigo',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.RunPython(
            code=asignar_codigos_legacy,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='producto',
            name='codigo',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
