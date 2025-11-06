# limpiar_archivo_whatsapp.py
# =======================================
# Limpia caracteres invisibles de los .txt exportados de WhatsApp
# y genera una versión "_LIMPIO.txt" en la misma carpeta
# =======================================

import os
from pathlib import Path
from limpieza_texto import limpiar_texto_whatsapp

def limpiar_archivo(ruta_original):
    """
    Limpia caracteres invisibles Unicode y guarda una copia limpia.
    Devuelve la ruta del nuevo archivo limpio.
    """
    if not os.path.exists(ruta_original):
        posible_ruta = os.path.join(os.path.dirname(__file__), "..", "chats_soporte", ruta_original)
        if os.path.exists(posible_ruta):
            ruta_original = posible_ruta
        else:
            print(f"[ERROR] No se encontró el archivo: {ruta_original}")
            return None

    ruta = Path(ruta_original)
    ruta_salida = ruta.with_name(ruta.stem + "_LIMPIO.txt")

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            lineas = f.readlines()

        lineas_limpias = [limpiar_texto_whatsapp(l) for l in lineas]

        with open(ruta_salida, "w", encoding="utf-8") as f:
            for l in lineas_limpias:
                if l.strip():
                    f.write(l.strip() + "\n")

        print(f"[OK] Archivo limpio generado: {ruta_salida.name}")
        return ruta_salida
    except Exception as e:
        print(f"[ERROR] No se pudo limpiar {ruta_original}: {e}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: py limpiar_archivo_whatsapp.py \"Chat de WhatsApp con XXX.txt\"")
    else:
        limpiar_archivo(sys.argv[1])
