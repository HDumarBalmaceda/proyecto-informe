# limpieza_texto.py
# ===============================
# Módulo para limpiar y normalizar texto de los chats de WhatsApp
# Elimina caracteres invisibles Unicode que rompen expresiones regulares
# ===============================

import re
import unicodedata

def limpiar_texto_whatsapp(texto: str) -> str:
    """
    Limpia caracteres invisibles o no imprimibles que suelen venir en los .txt exportados de WhatsApp.
    """
    if not texto:
        return texto

    # Normalizar forma canónica
    texto = unicodedata.normalize("NFC", texto)

    # Lista de caracteres invisibles comunes en WhatsApp
    caracteres_invisibles = [
        "\u200e",  # LEFT-TO-RIGHT MARK
        "\u200f",  # RIGHT-TO-LEFT MARK
        "\u202a",  # LEFT-TO-RIGHT EMBEDDING
        "\u202c",  # POP DIRECTIONAL FORMATTING
        "\u202d",  # LEFT-TO-RIGHT OVERRIDE
        "\u202e",  # RIGHT-TO-LEFT OVERRIDE
        "\ufeff",  # ZERO WIDTH NO-BREAK SPACE (BOM)
        "\u00a0",  # NO-BREAK SPACE
        "\u202f",  # NARROW NO-BREAK SPACE (usa WhatsApp para “a. m.” y “p. m.”)
    ]

    for c in caracteres_invisibles:
        texto = texto.replace(c, " ")

    # Quitar espacios duplicados o mezclas extrañas
    texto = re.sub(r"\s{2,}", " ", texto)

    # Limpiar bordes
    return texto.strip()


# --- Prueba rápida ---
if __name__ == "__main__":
    ejemplo = "22/7/2025, 11:39 a. m. - Soporte donucol: Hola 👋"
    print("Antes:", ejemplo)
    print("Después:", limpiar_texto_whatsapp(ejemplo))
