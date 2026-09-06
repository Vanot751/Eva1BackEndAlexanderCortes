from django.db import migrations, models


def asignar_codigos_legacy(apps, schema_editor):
    producto_model = apps.get_model('inventario', 'Producto')
    for producto in producto_model.objects.all():
        producto.codigo = f'LEGACY-{producto.pk:06d}'
        producto.save(update_fields=['codigo'])


class Migration(migrations.Migration):
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
