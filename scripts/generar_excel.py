# generar_excel.py
# ===============================
# Genera un archivo Excel con el conteo de soportes por mes
# ===============================

import os
import re
import pandas as pd

def _sanitize_filename(name: str) -> str:
    # Elimina caracteres no válidos en Windows y limpia espacios/puntos finales
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', name)
    name = name.strip().rstrip('.')
    return name

def generar_excel(resultados, tipos_soporte, meses_map, nombre_archivo_txt):
    """
    Crea un archivo Excel con el mismo nombre del TXT en la carpeta 'informes'.
    Retorna la ruta del archivo generado (o None si no hay resultados).
    """
    df = pd.DataFrame(resultados)
    if df.empty:
        print("⚠️ No se encontraron soportes para este chat.")
        return None

    # Meses en orden español
    orden_meses = list(meses_map.values())

    # DataFrame base con todos los soportes y meses
    base = pd.DataFrame(0, index=tipos_soporte.keys(), columns=orden_meses)
    base.index.name = "SOPORTES"

    # Sumar valores reales
    conteo = df.groupby(["Tipo de Soporte", "Mes"]).size()
    for (soporte, mes), valor in conteo.items():
        mes_esp = meses_map.get(mes, mes)
        if soporte in base.index and mes_esp in base.columns:
            base.at[soporte, mes_esp] += valor

    # Convertir a DataFrame normal con SOPORTES como columna
    base.reset_index(inplace=True)

    # Añadir columna TOTAL
    base["TOTAL"] = base[orden_meses].sum(axis=1)

    # Reemplazar 0 con vacío para mejor legibilidad
    base = base.replace(0, "")

    # Crear carpeta 'informes' si no existe (ruta relativa al paquete)
    carpeta_informes = os.path.join(os.path.dirname(__file__), "..", "informes")
    carpeta_informes = os.path.abspath(carpeta_informes)
    os.makedirs(carpeta_informes, exist_ok=True)

    # Nombre base del archivo .txt (sanitizado)
    nombre_base = os.path.splitext(os.path.basename(nombre_archivo_txt))[0]
    nombre_base = _sanitize_filename(nombre_base)

    ruta_excel = os.path.join(carpeta_informes, f"{nombre_base}.xlsx")

    # Exportar a Excel
    base.to_excel(ruta_excel, index=False)
    print(f"✅ Informe generado correctamente: {ruta_excel}")
    return ruta_excel
