import pandas as pd
import os
from datetime import datetime
import Ventana_de_estado as ve

# =============================================================================
# PASO 1: PREPARACIÓN DE DATOS
# =============================================================================

# Traer el dataframe combinado para su procesamiento
def procesar_archivo(archcsv1):
    # Seleccionar solo las columnas necesarias para el procesamiento
    columnas_a_copiar = archcsv1[['Created at', 'Name', 'Shipping Name', 'Lineitem quantity', 'Lineitem name', 'Total', 'Shipping Province Name', 'Shipping Street', 'Shipping Zip', 'Shipping Phone', 'Email', 'Lineitem sku']].copy()

    # =============================================================================
    # PASO 2: FORMATEO DE FECHAS (SOLUCIÓN SIMPLE)
    # =============================================================================

    # Buscar primera fecha válida y convertir a DD-MM-YYYY
    fecha_arch_datetime = None
    for index, row in archcsv1.iterrows():
        try:
            fecha_candidata = row['Created at']
            if pd.notna(fecha_candidata):
                fecha_arch_datetime = pd.to_datetime(fecha_candidata, errors='raise')
                break
        except:
            continue
    
    if fecha_arch_datetime is None:
        fecha_arch_datetime = datetime.now()
    
    # Siempre formato DD-MM-YYYY para el nombre del archivo
    Fecha = fecha_arch_datetime.strftime('%d-%m-%Y')

    # Formatear todas las fechas en la columna para mostrar como DD/MM/YYYY
    columnas_a_copiar['Created at'] = pd.to_datetime(archcsv1['Created at'], errors='coerce')
    columnas_a_copiar['Created at'] = columnas_a_copiar['Created at'].dt.strftime('%d/%m/%Y')

    # =============================================================================
    # PASO 3: AGREGAR COLUMNAS PARA CATEGORIZACIÓN
    # =============================================================================

    # Calcular el número de filas para crear columnas vacías
    num_filas = len(archcsv1)

    # Crear columnas vacías para:
    nueva_columna1 = [""] * num_filas  # Status (categoría principal)
    nueva_columna2 = [""] * num_filas  # NC2 (no clasificado 2)
    nueva_columna3 = [""] * num_filas  # NC3 (no clasificado 3)
    nueva_columna4 = [""] * num_filas  # NC4 (no clasificado 4)

    # Insertar las nuevas columnas en posiciones específicas
    posicion_columna1 = 9   # Status después del teléfono
    posicion_columna2 = 10  # NC2
    posicion_columna3 = 11  # NC3  
    posicion_columna4 = 12  # NC4

    columnas_a_copiar.insert(posicion_columna1, "Status", nueva_columna1)
    columnas_a_copiar.insert(posicion_columna2, "NC2", nueva_columna2)
    columnas_a_copiar.insert(posicion_columna3, "NC3", nueva_columna3)
    columnas_a_copiar.insert(posicion_columna4, "NC4", nueva_columna4)

    # =============================================================================
    # PASO 4: LIMPIEZA DE DATOS - DNI/SHIPPING COMPANY
    # =============================================================================

    # Limpiar puntos y espacios del campo DNI/Shipping Company
    archcsv1['Shipping Company'] = archcsv1['Shipping Company'].astype(str).str.replace(".", "")
    archcsv1['Shipping Company'] = archcsv1['Shipping Company'].str.replace(" ", "")

    # =============================================================================
    # PASO 5: CATEGORIZACIÓN POR ESTADO FINANCIERO
    # =============================================================================
    # IMPORTANTE: Los bucles están separados intencionalmente para manejar 
    # diferentes prioridades de categorización. NO COMBINAR.

    # BUCLE 1: Categorización básica por estado financiero y validación DNI
    for index, row in archcsv1.iterrows():
        if isinstance(row['Shipping Company'], str) and row['Financial Status'] == 'paid':
            # Si el DNI empieza con "DNI " está bien formateado
            if row['Shipping Company'].startswith("DNI "):
                pass  # DNI válido, no hacer nada
            else:
                # Si no es numérico, marcar para revisión
                if not row['Shipping Company'].isnumeric():
                    columnas_a_copiar.loc[index, 'Status'] = "REVISAR DNI"
        
        # Estados financieros específicos
        elif row['Financial Status'] == 'expired':
            columnas_a_copiar.loc[index, 'Status'] = 'VENCIDO'
        elif row['Financial Status'] == 'refunded':
            columnas_a_copiar.loc[index,'Status'] = 'REEMBOLSADO'
        elif row['Financial Status'] == 'pending':
            columnas_a_copiar.loc[index, 'Status'] = "FALTA PAGAR"

    # =============================================================================
    # PASO 6: CATEGORIZACIÓN POR UBICACIÓN GEOGRÁFICA
    # =============================================================================

    # BUCLE 2: Identificar pedidos de CABA por código postal
    for index, row in archcsv1.iterrows():
        # Códigos postales de CABA: C10-C15 y variantes con comillas
        if row['Financial Status'] == 'paid' and str(row['Shipping Zip']).startswith(("C14","C11","C10","C12","C15","C13","'15","'14","'13","'12","'11","'10","15","14","13","12","11","10")):
            columnas_a_copiar.loc[index, 'Status'] = "CABA"
        else:
            # Envíos prioritarios (sin importar ubicación)
            if row['Financial Status'] == 'paid' and row['Shipping Method'] == 'Envío Prioritario + Garantía extendida':
                columnas_a_copiar.loc[index, 'Status'] = 'PRIORITARIO'

    # =============================================================================        
    # PASO 7: CATEGORIZACIÓN COMBINADA (CABA + PRIORITARIO)
    # =============================================================================

    # BUCLE 3: Casos especiales - CABA + Prioritario
    for index, row in archcsv1.iterrows():
        if row['Financial Status'] == 'paid' and row['Shipping Method'] == 'Envío Prioritario + Garantía extendida' and str(row['Shipping Zip']).startswith(("C14","C11","C10","C12","C15","C13","'15","'14","'13","'12","'11","'10","15","14","13","12","11","10")):
            columnas_a_copiar.loc[index, 'Status'] = 'CABA PRIORITARIO'

    # =============================================================================
    # PASO 8: CATEGORIZACIÓN POR NOTAS Y CASOS ESPECIALES
    # =============================================================================

    # BUCLE 4: Revisar notas y casos especiales geográficos
    for index, row in archcsv1.iterrows():
        note = row['Notes']
        # Si hay notas en el pedido, requiere revisión manual
        if row['Financial Status'] == 'paid' and pd.notnull(note) and note.strip():
            columnas_a_copiar.loc[index, 'Status'] = "REVISAR NOTAS EN SHOPIFY" 
        else:
            # Tierra del Fuego requiere manejo especial
            if row['Financial Status'] == 'paid' and row['Shipping Province Name'] == 'Tierra del Fuego':
                columnas_a_copiar.loc[index, 'Status'] = "TIERRA DEL FUEGO"

    # =============================================================================
    # PASO 9: UNIFICACIÓN DE STATUS POR PEDIDO
    # =============================================================================

    # Agrupar por 'Name' (número de pedido) y aplicar el mismo status a todas las líneas del pedido
    # Esto es importante porque un pedido puede tener múltiples productos (líneas)
    def assign_status(group):
        """Asigna el mismo status a todas las líneas de un pedido"""
        group['Status'] = group['Status'].iloc[0]  # Toma el status de la primera línea
        return group

    columnas_a_copiar = columnas_a_copiar.groupby('Name').apply(assign_status).reset_index(drop=True)

    # =============================================================================
    # PASO 10: FINALIZACIÓN Y LIMPIEZA
    # =============================================================================

    # Esta es la copia final que se exportará
    ArchivoFinal = columnas_a_copiar

    # Arreglar formato de números de teléfono (remover .0 de pandas)
    ArchivoFinal['Shipping Phone'] = ArchivoFinal['Shipping Phone'].astype(str).str.replace(".0", "")

    # =============================================================================
    # PASO 11: CÁLCULO DE ESTADÍSTICAS PARA LA INTERFAZ
    # =============================================================================

    # Contar pedidos por categoría
    caba_df = ArchivoFinal[ArchivoFinal['Status'].isin(['CABA'])]
    caba_count = len(caba_df['Name'].unique())

    falta_pagar_df = ArchivoFinal[ArchivoFinal['Status'] == 'FALTA PAGAR']
    falta_pagar_count = len(falta_pagar_df['Name'].unique())

    vencido_df = ArchivoFinal[ArchivoFinal['Status'] == 'VENCIDO']
    vencido_count = len(vencido_df['Name'].unique())

    reembolsado_df = ArchivoFinal[ArchivoFinal['Status'] == 'REEMBOLSADO']
    reembolsado_count = len(reembolsado_df['Name'].unique())

    notas_df = ArchivoFinal[ArchivoFinal['Status'] == 'REVISAR NOTAS EN SHOPIFY']
    notas_count = len(notas_df['Name'].unique())

    revisar_dni_df = ArchivoFinal[ArchivoFinal['Status'] == 'REVISAR DNI']
    revisar_dni_count = len(revisar_dni_df['Name'].unique())

    # Sin clasificar = pedidos pagados sin categoría específica (TAMBIÉN pedidos únicos)
    sin_clasificar_df = ArchivoFinal[ArchivoFinal['Status'] == '']
    sin_clasificar_count = len(sin_clasificar_df['Name'].unique())

    # Actualizar interfaz con estadísticas
    ve.actualizar_estadisticas(
        caba=caba_count,
        falta_pagar=falta_pagar_count, 
        vencido=vencido_count,
        reembolsado=reembolsado_count,
        sin_clasificar=sin_clasificar_count,
        notas=notas_count,
        revisar_dni=revisar_dni_count
    )

    return ArchivoFinal, Fecha
