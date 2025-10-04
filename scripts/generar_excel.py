# generar_excel.py
# ===============================
# Genera un archivo Excel con el conteo de soportes por mes
# ===============================

import pandas as pd

def generar_excel(resultados, tipos_soporte, meses_map):
    """
    Crea un archivo 'informe_soportes.xlsx' con los resultados clasificados.
    """
    df = pd.DataFrame(resultados)
    if df.empty:
        print("⚠️ No se encontraron soportes")
        return

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

    # Exportar a Excel
    base.to_excel("informe_soportes.xlsx", index=False)
    print("✅ Informe generado: informe_soportes.xlsx")
