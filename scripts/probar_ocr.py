import pytesseract
from PIL import Image
import cv2

# Si instalaste Tesseract en una ruta diferente, descomenta y ajusta:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ruta a tu imagen de prueba (ajústala según la ubicación)
ruta_imagen = r"WhatsApp Image 2025-09-05 at 2.50.34 PM (1).jpeg"  # cámbiala por el nombre real de tu imagen

# --- OCR con OpenCV + Tesseract ---
img = cv2.imread(ruta_imagen)
if img is None:
    print("[ERROR] No se pudo cargar la imagen. Verifica la ruta.")
else:
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    texto = pytesseract.image_to_string(gris, lang='spa')
    print("\n TEXTO EXTRAÍDO DE LA IMAGEN:\n")
    print(texto.strip() or "(No se detectó texto)")
