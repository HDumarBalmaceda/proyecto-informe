# crear_informe.py
# ===============================
# Script principal: procesa chats, audios, imágenes, transcribe, clasifica y genera el informe
# Mantiene el orden real de la conversación (texto + audios + imágenes)
# Se puede ejecutar para TODOS los .txt en la carpeta o para uno solo:
#   py crear_informe.py                     -> procesa todos los txt
#   py crear_informe.py "Mi chat.txt"      -> procesa sólo ese archivo
# ===============================

import os
import re
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Importar módulos auxiliares
from transcribir import transcribir_audio
from clasificar import clasificar_soporte, tipos_soporte
from generar_excel import generar_excel
from procesar_imagenes import extraer_texto_imagen, analizar_visualmente

# -------------------------------
# Configuración de rutas y formatos
# -------------------------------
RUTA_CHATS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chats_soporte"))
RUTA_AUDIOS = RUTA_CHATS   # donde están tus PTT-*.opus
RUTA_IMAGENES = RUTA_CHATS # donde están tus IMG-*.jpg o png
RUTA_TRANSCRIPCIONES = Path("transcripciones")
RUTA_TRANSCRIPCIONES.mkdir(exist_ok=True)

# Traducción de meses inglés → español
meses_map = {
    "January": "Enero", "February": "Febrero", "March": "Marzo",
    "April": "Abril", "May": "Mayo", "June": "Junio",
    "July": "Julio", "August": "Agosto", "September": "Septiembre",
    "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

# Regex para audios e imágenes
regex_audio = re.compile(r"PTT-(\d{8})-WA\d+\.opus", re.IGNORECASE)
regex_imagen = re.compile(r"IMG-(\d{8})-WA\d+\.(jpg|png|jpeg)", re.IGNORECASE)

# -------------------------------
# Lista de archivos a procesar (soporta argumento opcional para un solo chat)
# -------------------------------
if len(sys.argv) > 1:
    # El usuario indicó un archivo concreto (puede ser nombre o ruta)
    arg = sys.argv[1]
    # Si el argumento apunta a la ruta completa, úsala; si no, asume que está dentro de RUTA_CHATS
    if os.path.isabs(arg) or os.path.exists(arg):
        archivos_a_procesar = [arg]
    else:
        archivos_a_procesar = [os.path.join(RUTA_CHATS, arg)]
else:
    # Procesar todos los .txt en la carpeta
    archivos_a_procesar = [
        os.path.join(RUTA_CHATS, f) for f in os.listdir(RUTA_CHATS) if f.lower().endswith(".txt")
    ]

if not archivos_a_procesar:
    print("⚠️ No se encontraron archivos .txt en la carpeta de chats.")
    sys.exit(0)

# -------------------------------
# Procesar cada chat por separado (reseteando resultados por chat)
# -------------------------------
for ruta_txt in archivos_a_procesar:
    if not os.path.exists(ruta_txt):
        print(f"[ERROR] No existe el archivo: {ruta_txt}")
        continue

    nombre_txt = os.path.basename(ruta_txt)
    print(f"\n[DEBUG] Iniciando procesamiento del chat: {nombre_txt}")

    resultados = []  # <-- reiniciar para cada chat

    with open(ruta_txt, "r", encoding="utf-8") as f:
        for linea in f:
            # Intentar extraer la fecha (si no puede, se salta la línea)
            try:
                fecha = datetime.strptime(linea.split(",")[0], "%d/%m/%Y").date()
            except Exception:
                continue

            if fecha.year < 2025:
                continue

            texto_linea = linea.strip().lower()

            # --- Caso 1: Audio ---
            m_audio = regex_audio.search(linea)
            if m_audio:
                nombre_audio = m_audio.group(0)
                ruta_audio = os.path.join(RUTA_AUDIOS, nombre_audio)
                if os.path.exists(ruta_audio):
                    print(f"[DEBUG] Transcribiendo audio en orden: {nombre_audio}")
                    transcripcion = transcribir_audio(ruta_audio)

                    # Guardar transcripción
                    archivo_txt_trans = RUTA_TRANSCRIPCIONES / f"{Path(nombre_audio).stem}.txt"
                    with open(archivo_txt_trans, "w", encoding="utf-8") as ft:
                        ft.write(transcripcion)

                    soporte = clasificar_soporte(transcripcion) or "Adjunto (pendiente clasificar)"
                else:
                    print(f"[ADVERTENCIA] Audio no encontrado: {nombre_audio}")
                    soporte = "Adjunto (pendiente clasificar)"

                resultados.append({
                    "Fecha": fecha,
                    "Mes": meses_map.get(fecha.strftime("%B"), fecha.strftime("%B")),
                    "Año": fecha.year,
                    "Tipo de Soporte": soporte
                })
                continue

            # --- Caso 2: Imagen ---
            m_imagen = regex_imagen.search(linea)
            if m_imagen:
                nombre_imagen = m_imagen.group(0)
                ruta_imagen = os.path.join(RUTA_IMAGENES, nombre_imagen)
                if os.path.exists(ruta_imagen):
                    print(f"\n[DEBUG] Procesando imagen en orden: {nombre_imagen}")
                    texto_img = extraer_texto_imagen(ruta_imagen)

                    if texto_img:
                        soporte = clasificar_soporte(texto_img)
                        print(f"[OCR] Texto detectado en {nombre_imagen}: {texto_img[:100]}...")
                    else:
                        soporte = analizar_visualmente(ruta_imagen)
                        print(f"[VISUAL] No se detectó texto en {nombre_imagen}, clasificado por análisis visual.")

                    if not soporte:
                        soporte = "Imagen (pendiente clasificar)"
                else:
                    print(f"[ADVERTENCIA] Imagen no encontrada: {nombre_imagen}")
                    soporte = "Imagen no encontrada"

                print(f"[RESULTADO] {nombre_imagen} → {soporte}\n")

                resultados.append({
                    "Fecha": fecha,
                    "Mes": meses_map.get(fecha.strftime("%B"), fecha.strftime("%B")),
                    "Año": fecha.year,
                    "Tipo de Soporte": soporte
                })
                continue

            # --- Caso 3: Mensaje de texto (solo del cliente) ---
            if " - soporte donucol:" not in linea:
                soporte = clasificar_soporte(texto_linea) or "Adjunto (pendiente clasificar)"
                resultados.append({
                    "Fecha": fecha,
                    "Mes": meses_map.get(fecha.strftime("%B"), fecha.strftime("%B")),
                    "Año": fecha.year,
                    "Tipo de Soporte": soporte
                })

    # -------------------------------
    # Debug rápido antes de generar Excel (opcional)
    # -------------------------------
    df_debug = pd.DataFrame(resultados)
    print("\nPrimeros 10 registros obtenidos para este chat:\n")
    print(df_debug.head(10))
    print("\nConteo por Tipo de Soporte (parcial):\n")
    print(df_debug["Tipo de Soporte"].value_counts())

    # -------------------------------
    # Generar Excel para ESTE chat
    # -------------------------------
    ruta_generado = generar_excel(resultados, tipos_soporte, meses_map, ruta_txt)
    if ruta_generado:
        print(f"[OK] Informe guardado en: {ruta_generado}")
    else:
        print("[INFO] No se generó informe (no hubo datos).")
