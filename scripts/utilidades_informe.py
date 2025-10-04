# utilidades.py
# ===============================
# Funciones de apoyo (regex, extracción de fechas, indexación de audios, etc.)
# ===============================

import os
import re
from datetime import datetime

# Regex para fecha en líneas del chat
regex_fecha = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})")

def extraer_fecha_linea(linea: str):
    """
    Extrae la fecha de una línea de chat.
    Devuelve un objeto datetime.date o None.
    """
    m = regex_fecha.search(linea)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%d/%m/%Y").date()
    except:
        return None

def build_audio_index(ruta_txt, carpeta_audios, remitente_excluido="Soporte"):
    """
    Construye un índice { (fecha, hora, remitente) : ruta_audio } 
    a partir de los audios en la carpeta.
    """
    index = {}
    for archivo in os.listdir(carpeta_audios):
        if archivo.lower().endswith((".opus", ".ogg", ".mp3", ".m4a", ".wav")):
            # Formato esperado de WhatsApp: PTT-20250904-WA0008.opus
            # Se podría mejorar si definimos un parser de nombres
            ruta_audio = os.path.join(carpeta_audios, archivo)
            # De momento el indexado se llena manualmente desde crear_informe
            # (aquí se podría mejorar con metadatos si se usa datos_audios.py)
    return index
