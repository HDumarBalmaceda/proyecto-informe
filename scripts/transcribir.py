# transcribir.py
# ===============================
# Convierte audios en texto usando SpeechRecognition
# Convierte a WAV si es necesario y guarda transcripciones
# ===============================

import os
import subprocess
import speech_recognition as sr

CARPETA_TRANSCRIPCIONES = "../transcripciones"

# Asegurar que la carpeta exista
os.makedirs(CARPETA_TRANSCRIPCIONES, exist_ok=True)


def convertir_a_wav(ruta_audio: str) -> str:
    """
    Convierte un archivo de audio a WAV (16kHz, mono).
    Devuelve la ruta del archivo WAV generado.
    """
    ruta_wav = os.path.splitext(ruta_audio)[0] + "_temp.wav"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", ruta_audio, "-ar", "16000", "-ac", "1", ruta_wav],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return ruta_wav
    except Exception as e:
        print(f"[ERROR] No se pudo convertir {ruta_audio} a WAV: {e}")
        return None


def transcribir_audio(ruta_audio: str) -> str:
    """
    Transcribe un archivo de audio a texto (español).
    Si el formato no es compatible, convierte a WAV.
    Además guarda la transcripción en un archivo .txt
    dentro de la carpeta de transcripciones.
    """
    r = sr.Recognizer()
    texto = ""

    # Si no es WAV → convertir
    ruta_usable = ruta_audio
    if not ruta_audio.lower().endswith(".wav"):
        ruta_usable = convertir_a_wav(ruta_audio)
        if ruta_usable is None:
            return ""

    try:
        with sr.AudioFile(ruta_usable) as source:
            audio = r.record(source)
        texto = r.recognize_google(audio, language="es-ES")
    except Exception as e:
        print(f"[ERROR] No se pudo transcribir {ruta_audio}: {e}")
        texto = ""

    # Guardar transcripción en carpeta
    nombre = os.path.splitext(os.path.basename(ruta_audio))[0] + ".txt"
    ruta_salida = os.path.join(CARPETA_TRANSCRIPCIONES, nombre)
    try:
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(texto)
    except Exception as e:
        print(f"[ERROR] No se pudo guardar la transcripción de {ruta_audio}: {e}")

    # Eliminar temporal WAV si se generó
    if ruta_usable != ruta_audio and os.path.exists(ruta_usable):
        os.remove(ruta_usable)

    return texto
