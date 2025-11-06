# control_duplicados.py
# ===============================
# Control de duplicados por palabra clave
# Evita contar el mismo soporte varias veces dentro de un rango de tiempo
# ===============================

from datetime import datetime, timedelta

# Intervalo de tiempo para considerar un soporte como nuevo (en minutos)
INTERVALO_MINUTOS = 5

# Diccionario global para rastrear última mención por palabra clave
ultima_mencion = {}

def registrar_soporte(resultados, soporte, fecha_completa, fecha, meses_map):
    """
    Agrega un soporte si no fue mencionado en los últimos X minutos.
    Devuelve True si se registró, False si se ignoró.
    """
    palabra_clave = soporte.lower()
    if palabra_clave in ultima_mencion:
        diferencia = fecha_completa - ultima_mencion[palabra_clave]
        if diferencia < timedelta(minutes=INTERVALO_MINUTOS):
            # Ya se mencionó recientemente → se ignora
            return False

    # Registrar nuevo soporte
    ultima_mencion[palabra_clave] = fecha_completa
    resultados.append({
        "Fecha": fecha,
        "Mes": meses_map.get(fecha.strftime("%B"), fecha.strftime("%B")),
        "Año": fecha.year,
        "Tipo de Soporte": soporte
    })
    return True
