import os
from datetime import datetime

# Necesitamos mutagen para leer metadatos de opus
# Instálalo antes con:  pip install mutagen
from mutagen.oggopus import OggOpus

def get_opus_datetime(ruta_audio):
    """
    Extrae la fecha/hora del metadato creation_time de un archivo .opus
    Si no encuentra, usa la fecha/hora de modificación del archivo.
    """
    try:
        audio = OggOpus(ruta_audio)
        tags = audio.tags
        if tags:
            # WhatsApp suele usar 'creation_time'
            if 'creation_time' in tags:
                # convertir a datetime
                return datetime.fromisoformat(tags['creation_time'][0].replace('Z',''))
            elif 'DATE' in tags:
                return datetime.fromisoformat(tags['DATE'][0])
    except Exception as e:
        print(f"Error leyendo metadatos de {ruta_audio}: {e}")

    # Si no hay metadato, usar fecha/hora de modificación
    return datetime.fromtimestamp(os.path.getmtime(ruta_audio))


if __name__ == "__main__":
    # 🔹 Cambia aquí la ruta de tu audio de prueba
    ruta_audio = r"C:\Users\asistemas.DONUCOL\Desktop\proyecto informe\chats_soporte\PTT-20250904-WA0008.opus"

    if os.path.exists(ruta_audio):
        dt = get_opus_datetime(ruta_audio)
        print(f"\n📄 Archivo: {ruta_audio}")
        print(f"📅 Fecha y hora obtenida: {dt}")
    else:
        print("⚠️ No se encontró el archivo, revisa la ruta.")
