# crear_informe.py
# ===============================
# Procesa chats de WhatsApp: textos, audios e imágenes
# - Limpia automáticamente los .txt antes de procesarlos
# - Transcribe audios .opus
# - Extrae texto de imágenes
# - Clasifica cada soporte
# - Evita duplicados (±10 min)
# - Omite todos los mensajes enviados por "Soporte Donucol"
# ===============================

import os
import re
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Importar módulos auxiliares
from transcribir import transcribir_audio
from clasificar import clasificar_soporte, tipos_soporte
from generar_excel import generar_excel
from procesar_imagenes import extraer_texto_imagen, analizar_visualmente
from limpiar_archivo_whatsapp import limpiar_archivo  #  integración automática del limpiador

# -------------------------------
# Configuración
# -------------------------------
RUTA_CHATS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chats_soporte"))
RUTA_AUDIOS = RUTA_CHATS
RUTA_IMAGENES = RUTA_CHATS
RUTA_TRANSCRIPCIONES = Path("transcripciones")
RUTA_TRANSCRIPCIONES.mkdir(exist_ok=True)

# Mapeo de meses al español
meses_map = {
    "January": "Enero", "February": "Febrero", "March": "Marzo",
    "April": "Abril", "May": "Mayo", "June": "Junio",
    "July": "Julio", "August": "Agosto", "September": "Septiembre",
    "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

# Expresiones regulares
regex_audio = re.compile(r"PTT-(\d{8})-WA\d+\.opus", re.IGNORECASE)
regex_imagen = re.compile(r"IMG-(\d{8})-WA\d+\.(jpg|png|jpeg)", re.IGNORECASE)

# -------------------------------
# Control de duplicados
# -------------------------------
ultimo_registro = {}

def registrar_soporte(resultados, soporte, fecha_completa, fecha, meses_map):
    """Evita registrar el mismo tipo de soporte dentro de los 10 minutos siguientes."""
    global ultimo_registro
    tipo = soporte
    tiempo_ultimo = ultimo_registro.get(tipo)

    if tiempo_ultimo and abs((fecha_completa - tiempo_ultimo).total_seconds()) < 600:
        return False  # duplicado reciente, ignorar

    ultimo_registro[tipo] = fecha_completa
    resultados.append({
        "Fecha": fecha,
        "Mes": meses_map.get(fecha.strftime("%B"), fecha.strftime("%B")),
        "Año": fecha.year,
        "Tipo de Soporte": soporte
    })
    return True

# -------------------------------
# Detectar archivos a procesar
# -------------------------------
if len(sys.argv) > 1:
    arg = sys.argv[1]
    if os.path.isabs(arg) or os.path.exists(arg):
        archivos_a_procesar = [arg]
    else:
        archivos_a_procesar = [os.path.join(RUTA_CHATS, arg)]
else:
    archivos_a_procesar = [
        os.path.join(RUTA_CHATS, f)
        for f in os.listdir(RUTA_CHATS)
        if f.lower().endswith(".txt")
    ]

if not archivos_a_procesar:
    print(" No se encontraron archivos .txt en la carpeta de chats.")
    sys.exit(0)

# -------------------------------
# Procesar cada chat
# -------------------------------
for ruta_txt in archivos_a_procesar:
    if not os.path.exists(ruta_txt):
        print(f"[ERROR] No existe el archivo: {ruta_txt}")
        continue

    #  LIMPIEZA AUTOMÁTICA
    ruta_txt_limpio = limpiar_archivo(ruta_txt)
    if not ruta_txt_limpio:
        print(f"[ADVERTENCIA] No se pudo limpiar {ruta_txt}, se omite.")
        continue

    ruta_txt = ruta_txt_limpio  # usar la versión limpia en adelante

    nombre_txt = os.path.basename(ruta_txt)
    print(f"\n[DEBUG] Iniciando procesamiento del chat limpio: {nombre_txt}")
    resultados = []
    ultimo_registro = {}  # reset por chat

    with open(ruta_txt, "r", encoding="utf-8") as f:
        for linea in f:
            try:
                fecha = datetime.strptime(linea.split(",")[0], "%d/%m/%Y").date()
            except Exception:
                continue

            if fecha.year < 2025:
                continue

            texto_linea = linea.strip().lower()

            # Omitir todo lo enviado por Soporte Donucol
            if " - Soporte donucol:" in texto_linea:
                continue

            # --- Caso 1: Audio ---
            m_audio = regex_audio.search(linea)
            if m_audio:
                nombre_audio = m_audio.group(0)
                ruta_audio = os.path.join(RUTA_AUDIOS, nombre_audio)
                if os.path.exists(ruta_audio):
                    print(f"[DEBUG] Transcribiendo audio: {nombre_audio}")
                    transcripcion = transcribir_audio(ruta_audio)
                    archivo_txt_trans = RUTA_TRANSCRIPCIONES / f"{Path(nombre_audio).stem}.txt"
                    with open(archivo_txt_trans, "w", encoding="utf-8") as ft:
                        ft.write(transcripcion)
                    soporte = clasificar_soporte(transcripcion) or "Adjunto (pendiente clasificar)"
                else:
                    print(f"[ADVERTENCIA] Audio no encontrado: {nombre_audio}")
                    soporte = "Adjunto (pendiente clasificar)"

                registrar_soporte(resultados, soporte, datetime.combine(fecha, datetime.min.time()), fecha, meses_map)
                continue

            # --- Caso 2: Imagen ---
            m_imagen = regex_imagen.search(linea)
            if m_imagen:
                nombre_imagen = m_imagen.group(0)
                ruta_imagen = os.path.join(RUTA_IMAGENES, nombre_imagen)
                if os.path.exists(ruta_imagen):
                    print(f"[DEBUG] Procesando imagen: {nombre_imagen}")
                    texto_img = extraer_texto_imagen(ruta_imagen)
                    if texto_img:
                        soporte = clasificar_soporte(texto_img)
                        print(f"[OCR] Texto detectado en {nombre_imagen}: {texto_img[:100]}...")
                    else:
                        soporte = analizar_visualmente(ruta_imagen)
                        print(f"[VISUAL] Clasificación visual aplicada.")
                    soporte = soporte or "Imagen (pendiente clasificar)"
                else:
                    print(f"[ADVERTENCIA] Imagen no encontrada: {nombre_imagen}")
                    soporte = "Imagen no encontrada"

                registrar_soporte(resultados, soporte, datetime.combine(fecha, datetime.min.time()), fecha, meses_map)
                continue

            # --- Caso 3: Texto (solo cliente) ---
            soporte = clasificar_soporte(texto_linea) or "Adjunto (pendiente clasificar)"
            registrar_soporte(resultados, soporte, datetime.combine(fecha, datetime.min.time()), fecha, meses_map)

    # -------------------------------
    # Resultado final del chat
    # -------------------------------
    df_debug = pd.DataFrame(resultados)
    print("\nPrimeros 10 registros obtenidos:\n")
    print(df_debug.head(10))
    print("\nConteo por Tipo de Soporte:\n")
    print(df_debug["Tipos de Soporte"].value_counts())

    # Generar Excel
    ruta_generado = generar_excel(resultados, tipos_soporte, meses_map, ruta_txt)
    if ruta_generado:
        print(f"[OK] Informe guardado en: {ruta_generado}")
    else:
        print("[INFO] No se generó informe (no hubo datos).")
