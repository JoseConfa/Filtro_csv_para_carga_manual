"""
filtroAndreani.py
=================
Procesador de pedidos para formato específico de Andreani.

Este módulo procesa los datos de pedidos de Shopify y los adapta al formato
requerido por la empresa de logística Andreani. Realiza transformaciones
similares a FiltroArgentina.py pero con columnas adicionales específicas
para los requisitos de envío de Andreani.

Funcionalidades principales:
- Extracción y formateo de datos de envío
- Agregado de columnas específicas de Andreani (peso, dimensiones, etc.)
- Categorización de pedidos por estado y ubicación
- Limpieza y validación de datos de contacto
- Agrupación por número de pedido para consistencia

Diferencias con FiltroArgentina:
- Incluye columnas técnicas para logística (peso, dimensiones, valor declarado)
- Formato específico para integración con sistemas de Andreani
- Valores por defecto para datos de envío

Autor: Sistema de Gestión de Pedidos
"""

import pandas as pd
import os
from datetime import datetime

def procesar_archivo(archcsv2):
    """
    Procesa un DataFrame de pedidos de Shopify para formato Andreani.
    
    Esta función toma los datos exportados de Shopify y los transforma al formato
    específico requerido por Andreani, agregando columnas técnicas necesarias
    para el procesamiento logístico.
    
    Args:
        archcsv2 (pandas.DataFrame): DataFrame con datos de pedidos de Shopify
        
    Returns:
        tuple: (DataFrame procesado, fecha del archivo en formato DD-MM-YYYY)
        
    Proceso de transformación:
        1. Extracción de fecha del archivo
        2. Selección de columnas relevantes para Andreani
        3. Agregado de columnas técnicas (peso, dimensiones, valor declarado)
        4. Limpieza y validación de datos
        5. Categorización por estado financiero y ubicación
        6. Agrupación por número de pedido
        7. Formateo final
    """
    
    # === PASO 1: EXTRACCIÓN DE FECHA DEL ARCHIVO ===
    
    # Buscar la primera fecha válida en la columna 'Created at' para nombrar el archivo
    fecha_arch_datetime = None
    
    for index, row in archcsv2.iterrows():
        try:
            fecha_candidata = row['Created at']
            if pd.notna(fecha_candidata):
                # pd.to_datetime maneja automáticamente múltiples formatos de fecha
                fecha_arch_datetime = pd.to_datetime(fecha_candidata, errors='raise')
                break
        except:
            continue
    
    # Si no se encuentra fecha válida, usar fecha actual como respaldo
    if fecha_arch_datetime is None:
        fecha_arch_datetime = datetime.now()
    
    # Convertir a formato DD-MM-YYYY para consistencia en nombres de archivo
    fecha_del_archivo = fecha_arch_datetime.strftime('%d-%m-%Y')

    # === PASO 2: SELECCIÓN Y PREPARACIÓN DE COLUMNAS ===
    
    # Seleccionar las columnas de interés específicas para Andreani y crear copia independiente
    columnas_a_copiar2 = archcsv2[['Name','Shipping Name','Shipping Company','Email','Shipping Phone','Shipping Street','Shipping Address2','Shipping City','Shipping Zip','Shipping Province Name','Notes']].copy()

    # Calcular número de filas para crear columnas adicionales del mismo tamaño
    num_filas = len(archcsv2)

    # === PASO 3: CREACIÓN DE COLUMNAS ESPECÍFICAS DE ANDREANI ===
    
    # Crear columnas vacías para datos técnicos requeridos por Andreani
    nueva_columna1 = [""] * num_filas  # Peso del paquete
    nueva_columna2 = [""] * num_filas  # Alto del paquete  
    nueva_columna3 = [""] * num_filas  # Ancho del paquete
    nueva_columna4 = [""] * num_filas  # Profundidad del paquete
    nueva_columna5 = [""] * num_filas  # Valor declarado
    nueva_columna6 = [""] * num_filas  # Status del pedido
    nueva_columna7 = [""] * num_filas  # Campo auxiliar NC
    nueva_columna8 = [""] * num_filas  # Código numérico

    # Definir las posiciones donde insertar las nuevas columnas en el DataFrame
    posicion_columna1 = 1   # Peso después de Name
    posicion_columna2 = 2   # Alto  
    posicion_columna3 = 3   # Ancho
    posicion_columna4 = 4   # Profundidad
    posicion_columna5 = 5   # Valor declarado
    posicion_columna6 = 6   # Status
    posicion_columna7 = 8   # NC (después de Shipping Name)
    posicion_columna8 = 11  # Código numérico

    # Insertar las nuevas columnas en el DataFrame en las posiciones especificadas
    columnas_a_copiar2.insert(posicion_columna1, "Peso", nueva_columna1)
    columnas_a_copiar2.insert(posicion_columna2, "Alto", nueva_columna2)
    columnas_a_copiar2.insert(posicion_columna3, "Ancho", nueva_columna3)
    columnas_a_copiar2.insert(posicion_columna4, "Profun", nueva_columna4)
    columnas_a_copiar2.insert(posicion_columna5, "Val decl", nueva_columna5)
    columnas_a_copiar2.insert(posicion_columna6, "Status", nueva_columna6)
    columnas_a_copiar2.insert(posicion_columna7, "NC", nueva_columna7)
    columnas_a_copiar2.insert(posicion_columna8, "CodNum", nueva_columna8)

    # === PASO 4: LIMPIEZA DE DATOS ===
    
    # Limpiar puntos y espacios del campo DNI/Shipping Company para validación
    archcsv2['Shipping Company'] = archcsv2['Shipping Company'].astype(str).str.replace(".", "")
    archcsv2['Shipping Company'] = archcsv2['Shipping Company'].astype(str).str.replace(" ", "")

    # Limpiar valores NaN en nombres de destinatario, manteniendo cadenas vacías
    archcsv2['Shipping Name'] = archcsv2['Shipping Name'].fillna("")

    # Limpiar teléfonos, reemplazando "nan" por cadena vacía
    archcsv2['Shipping Phone'] = archcsv2['Shipping Phone'].astype(str).str.replace("nan", "")

    # === PASO 5: CATEGORIZACIÓN POR ESTADO FINANCIERO ===
    
    # BUCLE 1: Categorización básica por estado financiero y validación de DNI
    # Este bucle maneja los pedidos pagados y valida el formato del DNI
    for index, row in archcsv2.iterrows():
        if isinstance(row['Shipping Company'], str) and row['Financial Status'] == 'paid':
            # Verificar si el DNI tiene el formato correcto "DNI XXXXXXXX"
            if row['Shipping Company'].startswith("DNI "):
                pass  # DNI válido, no requiere acción
            else:
                # Si no es numérico después de limpiar, requiere revisión manual
                if not row['Shipping Company'].isnumeric():
                    columnas_a_copiar2.loc[index, 'Status'] = "REVISAR DNI"

        # Manejar estados financieros específicos
        elif row['Financial Status'] == 'expired':
            columnas_a_copiar2.loc[index, 'Status'] = 'VENCIDO'
        elif row['Financial Status'] == 'refunded':
            columnas_a_copiar2.loc[index,'Status'] = 'REEMBOLSADO'
        elif row['Financial Status'] == 'pending':
            columnas_a_copiar2.loc[index, 'Status'] = "FALTA PAGAR"
        # Los pedidos pagados sin problemas de DNI quedan sin categoría específica

    # === PASO 6: CATEGORIZACIÓN POR UBICACIÓN GEOGRÁFICA ===
    
    # BUCLE 2: Identificar pedidos de CABA por código postal y envíos prioritarios
    for index, row in archcsv2.iterrows():
        # Códigos postales de CABA: C10-C15 y variantes con comillas y sin C
        if row['Financial Status'] == 'paid' and str(row['Shipping Zip']).startswith(("C14","C11","C10","C12","C15","C13","'15","'14","'13","'12","'11","'10","15","14","13","12","11","10")):
            columnas_a_copiar2.loc[index, 'Status'] = "CABA"
        else:
            # Identificar envíos prioritarios (independientemente de ubicación)
            if row['Financial Status'] == 'paid' and row['Shipping Method'] == 'Envío Prioritario + Garantía extendida':
                columnas_a_copiar2.loc[index, 'Status'] = 'PRIORITARIO'
            
    # === PASO 7: CATEGORIZACIÓN COMBINADA (CABA + PRIORITARIO) ===
    
    # BUCLE 3: Casos especiales - Pedidos que son tanto de CABA como prioritarios
    for index, row in archcsv2.iterrows():
        if row['Financial Status'] == 'paid' and row['Shipping Method'] == 'Envío Prioritario + Garantía extendida' and str(row['Shipping Zip']).startswith(("C14","C11","C10","C12","C15","C13","'15","'14","'13","'12","'11","'10","15","14","13","12","11","10")):
            columnas_a_copiar2.loc[index, 'Status'] = 'CABA PRIORITARIO'

    # === PASO 8: CATEGORIZACIÓN POR NOTAS Y CASOS ESPECIALES ===
    
    # BUCLE 4: Revisar notas del pedido y casos geográficos especiales
    for index, row in archcsv2.iterrows():
        note = row['Notes']
        # Si el pedido tiene notas, requiere revisión manual para instrucciones especiales
        if row['Financial Status'] == 'paid' and pd.notnull(note) and note.strip():
            columnas_a_copiar2.loc[index, 'Status'] = "REVISAR NOTAS EN SHOPIFY" 
        else:
            # Tierra del Fuego requiere manejo especial por ubicación geográfica
            if row['Financial Status'] == 'paid' and row['Shipping Province Name'] == 'Tierra del Fuego':
                columnas_a_copiar2.loc[index, 'Status'] = "TIERRA DEL FUEGO"

    # === PASO 9: ASIGNACIÓN DE VALORES TÉCNICOS DE ANDREANI ===
    
    # BUCLE 5: Asignar valores por defecto para todos los campos técnicos de Andreani
    # Estos valores son estándar para todos los pedidos según especificaciones de Andreani
    for index, row in archcsv2.iterrows():
        columnas_a_copiar2.loc[index, 'Peso'] = "100"      # Peso en gramos
        columnas_a_copiar2.loc[index, 'Alto'] = "10"       # Alto en cm
        columnas_a_copiar2.loc[index, 'Ancho'] = "15"      # Ancho en cm  
        columnas_a_copiar2.loc[index, 'Profun'] = "10"     # Profundidad en cm
        columnas_a_copiar2.loc[index, 'Val decl'] = "4500" # Valor declarado en pesos
        columnas_a_copiar2.loc[index, 'NC'] = "."          # Campo auxiliar
        columnas_a_copiar2.loc[index, 'CodNum'] = "54"     # Código numérico de Argentina

    # === PASO 10: UNIFICACIÓN DE STATUS POR PEDIDO ===
    
    # Agrupar por número de pedido ('Name') y aplicar el mismo status a todas las líneas del pedido
    # Esto es crucial porque un pedido puede tener múltiples productos (líneas)
    def assign_status(group):
        """
        Función auxiliar para asignar el mismo status a todas las líneas de un pedido.
        Toma el status de la primera línea y lo aplica a todo el grupo.
        """
        group['Status'] = group['Status'].iloc[0]
        return group

    columnas_a_copiar2 = columnas_a_copiar2.groupby('Name').apply(assign_status).reset_index(drop=True)

    # === PASO 11: PREPARACIÓN DEL ARCHIVO FINAL ===
    
    # Crear el DataFrame final que será exportado
    ArchivoFinal2 = columnas_a_copiar2

    # Limpiar formato de números de teléfono (remover .0 agregado por pandas)
    ArchivoFinal2['Shipping Phone'] = ArchivoFinal2['Shipping Phone'].astype(str).str.replace(".0", "")

    return ArchivoFinal2, fecha_del_archivo