# procesar_imagenes.py
# =========================
# Extrae texto de imágenes y genera etiquetas visuales simples

import cv2
import pytesseract
from PIL import Image

# Opcional: si no está en PATH, descomenta esta línea y ajusta la ruta de instalación
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extraer_texto_imagen(ruta_imagen):
    """
    Aplica OCR a la imagen para extraer texto (en español).
    Retorna el texto encontrado o una cadena vacía.
    """
    try:
        img = cv2.imread(ruta_imagen)
        if img is None:
            print(f"[ADVERTENCIA] No se pudo abrir la imagen: {ruta_imagen}")
            return ""

        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        texto = pytesseract.image_to_string(gris, lang='spa')
        texto_limpio = texto.strip()

        # Mostrar en consola qué se extrajo
        if texto_limpio:
            print(f"[OCR] Texto detectado en {ruta_imagen}:\n→ {texto_limpio[:100]}...\n")
        else:
            print(f"[OCR] Sin texto visible en {ruta_imagen}")

        return texto_limpio

    except Exception as e:
        print(f"[ERROR OCR] {ruta_imagen}: {e}")
        return ""


def analizar_visualmente(ruta_imagen):
    """
    Usa heurísticas simples: detección de bordes y formas
    para dar una pista del tipo de imagen (pantallazo, documento, etc.)
    """
    try:
        img = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"[ADVERTENCIA] No se pudo analizar visualmente: {ruta_imagen}")
            return "Imagen desconocida"

        bordes = cv2.Canny(img, 100, 200)
        densidad = (bordes > 0).mean()

        if densidad > 0.15:
            tipo = "Pantallazo o interfaz"
        elif densidad > 0.05:
            tipo = "Documento o formulario"
        else:
            tipo = "Imagen genérica"

        print(f"[ANÁLISIS] {ruta_imagen}: {tipo}")
        return tipo

    except Exception as e:
        print(f"[ERROR Análisis visual] {ruta_imagen}: {e}")
        return "Imagen desconocida"
