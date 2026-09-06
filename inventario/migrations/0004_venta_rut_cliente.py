from django.db import migrations, models


class Migration(migrations.Migration):
    # Conserva en cada venta el RUT usado para la boleta, incluso sin cliente habitual.
    dependencies = [
        ('inventario', '0003_producto_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='rut_cliente',
            field=models.CharField(default='SIN-RUT', max_length=12),
            preserve_default=False,
        ),
    ]
