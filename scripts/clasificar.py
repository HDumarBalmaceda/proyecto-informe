# clasificar.py
# ===============================
# Diccionario de soportes y palabras clave
# Función que clasifica un mensaje en un tipo de soporte
# ===============================

tipos_soporte = {
    "Impresora y Cajon": ["impresora", "cajón", "cajon"],
    "UPS": ["ups"],
    "Equipo Fisico": ["torre", "pantalla", "cpu", "equipo", "computador"],
    "Perifericos": ["mouse", "teclado", "cable"],
    "FrontRest": ["frontrest", "pos", "front", "cambio de clave", "cambiando la clave"],
    "SQL": ["sql", "minutas", "sql server"],
    "Creacion de usuario": ["crear usuario", "usuario nuevo", "registro", "huella", "auxiliar nuevo", "usuario de chico nuevo"],
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
    "Soporte Biometrico": ["ayudar con biometrico", "no muestra las marcaciones"],
    "Creacion de Promociones": ["promocion", "descuento especial", "no aparece la promocion"],
    "Compra de Equipos": ["comprar equipo", "compra computador"],
    "Inventarios": ["inventario", "baja", "traslado"],
    "Pedidos de suministros": ["suministro", "pedido insumo"],
    "Soporte con proveedores": ["claro", "etb", "tigo", "appitec"],
    "Informes": ["informe", "reporte", "sacar informe", "me ayudas con el informe"],
    "Cambio de precios": ["cambio precio", "precio"],
    "Soporte a Legis": ["legis"],
    "Soporte Manager": ["manager", "no tengo icg"],
    "Vencimiento del Dominio": ["dominio vencido"],
    "Soporte de Correo": ["correo", "email", "outlook", "me ayudan con el correo", "no tengo correo"],
    "Backup": ["backup", "copia seguridad", "no encuentro un archivo"],
    "Eventos": ["video beam", "sonido", "evento", "me ayudan a poner musica", "me ayudan con el audio"],
    "Actualizacion de Resoluciones pv": ["resolucion", "vencio la resolucion"],
    "Aperturas de Pv": ["apertura punto", "abrir pv"],
    "Sincronizacion de Suministros": ["sincronizacion suministros"],
    "Sincronizacion de ventas": ["sincronizacion ventas"],
    "Factura Electronica": ["factura electronica", "facturacion electronica"],
    "Capacitaciones": ["capacitacion", "entrenamiento"],
    "Soporte plataformas": ["didi", "rappi", "justo"],
    "Office": ["office", "word", "excel", "powerpoint"],
    "Adjunto (pendiente clasificar)": []
}

def clasificar_soporte(mensaje: str) -> str:
    """
    Clasifica un mensaje en un tipo de soporte según las palabras clave.
    Si no encuentra coincidencia, devuelve 'Adjunto (pendiente clasificar)'.
    """
    mensaje = mensaje.lower()
    for tipo, palabras in tipos_soporte.items():
        if any(p in mensaje for p in palabras):
            return tipo
    return "Adjunto (pendiente clasificar)"
