def validar_rut(rut):
    """Valida formato de RUT chileno (ej: 12345678-9 o 123456789)"""
    import re
    rut = rut.replace('.', '').replace('-', '')
    if not re.match(r'^\d{7,8}\d?$', rut):  # entre 7 y 8 dígitos + dígito verificador
        return False
    # Si quieres validar el dígito verificador, puedes implementar el algoritmo,
    # pero por simplicidad y para no complicar, solo verificamos el formato.
    return True