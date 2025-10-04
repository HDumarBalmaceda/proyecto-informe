# crear_informe.py
# ===============================
# Script principal: procesa chats, audios, transcribe, clasifica y genera el informe
# ===============================

import os
import re
import pandas as pd
from pathlib import Path
from datetime import datetime

# Importar módulos auxiliares
from transcribir import transcribir_audio
from clasificar import clasificar_soporte, tipos_soporte
from generar_excel import generar_excel

# -------------------------------
# Configuración de rutas y formatos
# -------------------------------
RUTA_CHATS = "../chats_soporte"
RUTA_AUDIOS = "../chats_soporte"   # donde están tus PTT-*.opus
RUTA_TRANSCRIPCIONES = Path("transcripciones")
RUTA_TRANSCRIPCIONES.mkdir(exist_ok=True)

# Traducción de meses inglés → español
meses_map = {
    "January": "Enero", "February": "Febrero", "March": "Marzo",
    "April": "Abril", "May": "Mayo", "June": "Junio",
    "July": "Julio", "August": "Agosto", "September": "Septiembre",
    "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

# Regex para audios PTT-YYYYMMDD-WA####.opus
regex_audio = re.compile(r"PTT-(\d{8})-WA\d+\.opus", re.IGNORECASE)

# Lista de resultados finales
resultados = []

# -------------------------------
# Procesar todos los audios encontrados
# -------------------------------
for archivo in os.listdir(RUTA_AUDIOS):
    match = regex_audio.match(archivo)
    if not match:
        continue

    fecha_str = match.group(1)  # ejemplo "20250904"
    fecha = datetime.strptime(fecha_str, "%Y%m%d").date()

    # Solo tomar audios de 2025 en adelante
    if fecha.year < 2025:
        continue

    ruta_audio = os.path.join(RUTA_AUDIOS, archivo)
    print(f"[DEBUG] Procesando audio: {archivo} ({fecha})")

    # -------------------------------
    # Transcripción
    # -------------------------------
    transcripcion = transcribir_audio(ruta_audio)

    # Guardar transcripción en carpeta
    archivo_txt = RUTA_TRANSCRIPCIONES / f"{Path(archivo).stem}.txt"
    with open(archivo_txt, "w", encoding="utf-8") as f:
        f.write(transcripcion)

    print(f"[DEBUG] Transcripción guardada en {archivo_txt}")

    # -------------------------------
    # Clasificación
    # -------------------------------
    soporte = clasificar_soporte(transcripcion)
    if soporte is None:
        soporte = "Adjunto (pendiente clasificar)"

    # Guardar resultado
    resultados.append({
        "Fecha": fecha,
        "Mes": meses_map.get(fecha.strftime("%B"), fecha.strftime("%B")),
        "Año": fecha.year,
        "Tipo de Soporte": soporte
    })

# -------------------------------
# Procesar también los chats de texto
# -------------------------------
for archivo in os.listdir(RUTA_CHATS):
    if not archivo.endswith(".txt"):
        continue

    ruta_txt = os.path.join(RUTA_CHATS, archivo)
    print(f"\n[DEBUG] Procesando chat: {archivo}")

    with open(ruta_txt, "r", encoding="utf-8") as f:
        for linea in f:
            # Saltar mensajes de soporte
            if " - Soporte donucol:" in linea:
                continue

            # Intentar extraer fecha
            try:
                fecha = datetime.strptime(linea.split(",")[0], "%d/%m/%Y").date()
            except Exception:
                continue

            if fecha.year < 2025:
                continue

            texto = linea.lower()
            soporte = clasificar_soporte(texto) or "Adjunto (pendiente clasificar)"

            resultados.append({
                "Fecha": fecha,
                "Mes": meses_map.get(fecha.strftime("%B"), fecha.strftime("%B")),
                "Año": fecha.year,
                "Tipo de Soporte": soporte
            })

# -------------------------------
# Depuración antes de generar Excel
# -------------------------------
df_debug = pd.DataFrame(resultados)
print("\nPrimeros 20 registros obtenidos:\n")
print(df_debug.head(20))
print("\nConteo por Tipo de Soporte:\n")
print(df_debug["Tipo de Soporte"].value_counts())

# -------------------------------
# Generar Excel final
# -------------------------------
generar_excel(resultados, tipos_soporte, meses_map)
print("✅ Informe generado: informe_soportes.xlsx")
