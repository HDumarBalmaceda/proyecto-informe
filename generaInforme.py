import os
import re
import pandas as pd
from datetime import datetime, date
import whisper
import json

# ---------------- CONFIG ----------------
RUTA_CHATS = "chats_soporte/"   # Carpeta con los .txt y audios
EXT_AUDIO = (".opus", ".ogg", ".mp3", ".m4a", ".wav")
CACHE_DIR = os.path.join(RUTA_CHATS, "transcripciones")

# Cargar modelo Whisper (elige "base", "small" o "medium")
modelo_audio = whisper.load_model("base")
# ----------------------------------------

#  Diccionario de palabras clave
tipos_soporte = {
    "Impresora y Cajon": ["impresora", "cajón", "cajon", ""],
    "UPS": ["ups"],
    "Equipo Fisico": ["torre", "pantalla", "cpu", "equipo", "computador"],
    "Perifericos": ["mouse", "teclado", "cable"],
    "FrontRest": ["frontrest", "pos", "front", "cambio de clave","cambiando la clave"],
    "SQL": ["sql", "minutas", "SQL Server"],
    "Creacion de usuario": ["crear usuario", "usuario nuevo", "registro", "huella", "auxiliar nuevo","usuario de chico nuevo"],
    "Actualizacion de SAP": ["actualizacion sap", "actualizar sap"],
    "Descuadres de Facturas": ["factura mal", "descuadre", "nota credito", "abono"],
    "Consumos con Valor": ["consumo con valor"],
    "Soporte Sap": ["sap", "caido sap", "sap no funciona"],
    "Soporte Biable": ["biable"],
    "Cambio de Discos": ["disco duro", "cambio disco"],
    "Soporte Renta sistemas": ["renta sistemas para revisar"],
    "Instalacion Swich": ["swich", "switch", "cambio swich"],
    "Soporte de Red": ["red", "internet", "conexion", "cableado", "no tengo internet"],
    "Instalacion Biometrico": ["biometrico", "huella"],
    "Soporte Biometrico":  ["ayudar con biometrico","no muestra las marcaciones"],
    "Creacion de Promociones": ["promocion", "descuento especial", "no aparece la promocion"],
    "Compra de Equipos": ["comprar equipo", "compra computador"],
    "Inventarios": ["inventario", "baja", "traslado"],
    "Pedidos de suministros": ["suministro", "pedido insumo"],
    "Soporte con proveedores": ["claro", "etb", "tigo", "appitec"],
    "Informes": ["informe", "reporte", "sacar informe", "me ayudas con el informe"],
    "Cambio de precios": ["cambio precio", "precio"],
    "Soporte a Legis": ["legis"],
    "Soporte Manager": ["manager", "no tengo icg",],
    "Vencimiento del Dominio": ["dominio vencido"],
    "Soporte de Correo": ["correo", "email", "outlook", "me ayudan con el correo", "no tengo correo"],
    "Backup": ["backup", "copia seguridad", "no encuentro un archivo"],
    "Eventos": ["video beam", "sonido", "evento", "me ayudan a poner musica", "me ayudan con el audio"],
    "Actualizacion de Resoluciones pv": ["resolucion","vencio la resolucion"],
    "Aperturas de Pv": ["apertura punto", "abrir pv"],
    "Sincronizacion de Suministros": ["sincronizacion suministros"],
    "Sincronizacion de ventas": ["sincronizacion ventas"],
    "Factura Electronica": ["factura electronica", "facturacion electronica"],
    "Capacitaciones": ["capacitacion", "entrenamiento"],
    "Soporte plataformas": ["didi", "rappi", "justo"],
    "Office": ["office", "word", "excel", "powerpoint"],
    "Adjunto (pendiente clasificar)": []
}

#  Traducción de meses
meses_map = {
    "January": "Enero", "February": "Febrero", "March": "Marzo",
    "April": "Abril", "May": "Mayo", "June": "Junio",
    "July": "Julio", "August": "Agosto", "September": "Septiembre",
    "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

# ---------------- FUNCIONES ----------------
def clasificar_soporte(mensaje):
    mensaje = mensaje.lower()
    for tipo, palabras in tipos_soporte.items():
        for p in palabras:
            if p in mensaje:
                return tipo
    return None

def find_date_in_filename(fname):
    """Busca fecha YYYYMMDD en nombre de archivo"""
    m = re.search(r"(\d{8})", fname)
    if m:
        try:
            return date(int(m.group(1)[:4]), int(m.group(1)[4:6]), int(m.group(1)[6:]))
        except:
            return None
    return None

def build_audio_index(folder):
    """Crea índice {fecha: [lista de audios]}"""
    idx = {}
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(EXT_AUDIO):
                ruta = os.path.join(root, f)
                d = find_date_in_filename(f)
                if d is None:
                    d = datetime.fromtimestamp(os.path.getmtime(ruta)).date()
                idx.setdefault(d, []).append(ruta)
    for k in idx:
        idx[k] = sorted(idx[k])
    return idx

def transcribe_audio(ruta_audio):
    """Transcribe audio con Whisper y usa cache"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    clave = os.path.splitext(os.path.basename(ruta_audio))[0]
    cache_file = os.path.join(CACHE_DIR, f"{clave}.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as fh:
            return json.load(fh).get("text", "")
    res = modelo_audio.transcribe(ruta_audio, language="es")
    texto = res.get("text", "").strip()
    with open(cache_file, "w", encoding="utf-8") as fh:
        json.dump({"text": texto}, fh, ensure_ascii=False)
    return texto
# -------------------------------------------

# Construir índice de audios
print("Cargando audios...")
audio_index = build_audio_index(RUTA_CHATS)

# Regex para fechas en WhatsApp
regex_fecha = re.compile(r"(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2})")

resultados = []

# Leer todos los chats
for archivo in os.listdir(RUTA_CHATS):
    if archivo.endswith(".txt"):
        ruta = os.path.join(RUTA_CHATS, archivo)
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                match = regex_fecha.match(linea)
                if match:
                    fecha_str = match.group(1)
                    try:
                        fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
                        if fecha.year >= 2025:
                            texto = linea.lower()

                            # --- Caso audio ---
                            if "<audio omitido>" in texto:
                                fecha_key = fecha.date()
                                archivo_audio = None
                                if fecha_key in audio_index and audio_index[fecha_key]:
                                    archivo_audio = audio_index[fecha_key].pop(0)
                                if archivo_audio:
                                    texto_trans = transcribe_audio(archivo_audio)
                                    print(f"🎤 Audio transcrito ({archivo_audio}): {texto_trans}")  # 👈 depuración
                                    soporte = clasificar_soporte(texto_trans)
                                    if not soporte:
                                        soporte = "Adjunto (pendiente clasificar)"
                                else:
                                    soporte = "Adjunto (pendiente clasificar)"

                                resultados.append({
                                    "Fecha": fecha,
                                    "Mes": meses_map.get(fecha.strftime("%B"), fecha.strftime("%B")),
                                    "Año": fecha.year,
                                    "Tipo de Soporte": soporte
                                })
                                continue

                            # --- Caso texto ---
                            soporte = clasificar_soporte(linea)
                            if soporte:
                                resultados.append({
                                    "Fecha": fecha,
                                    "Mes": meses_map.get(fecha.strftime("%B"), fecha.strftime("%B")),
                                    "Año": fecha.year,
                                    "Tipo de Soporte": soporte
                                })
                    except:
                        continue

# DataFrame
df = pd.DataFrame(resultados)
print("Total registros:", len(df))

if not df.empty:
    tabla = df.groupby(["Tipo de Soporte", "Mes"]).size().unstack(fill_value=0)

    # Orden de meses
    orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    tabla = tabla.reindex(columns=orden_meses, fill_value=0)

    # Total
    tabla["TOTAL"] = tabla.sum(axis=1)

    # Index a columna
    tabla.reset_index(inplace=True)
    tabla.rename(columns={"Tipo de Soporte": "SOPORTES"}, inplace=True)

    # Reemplazar ceros con vacío
    tabla = tabla.replace(0, "")

    # Asegurar todos los tipos
    for soporte in tipos_soporte.keys():
        if soporte not in tabla["SOPORTES"].values:
            fila = {c: "" for c in tabla.columns}
            fila["SOPORTES"] = soporte
            fila["TOTAL"] = ""
            tabla = pd.concat([tabla, pd.DataFrame([fila])], ignore_index=True)

    # Ordenar según el diccionario
    tabla["SOPORTES"] = pd.Categorical(tabla["SOPORTES"], categories=tipos_soporte.keys(), ordered=True)
    tabla = tabla.sort_values("SOPORTES").reset_index(drop=True)

    # Guardar
    tabla.to_excel("informe_soportes.xlsx", index=False)
    print("✅ Informe generado: informe_soportes.xlsx")
else:
    print("⚠️ No se encontraron soportes")
