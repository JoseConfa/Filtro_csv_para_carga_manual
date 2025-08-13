"""
excel_concat.py
===============
Generador de archivos Excel unificados con múltiples hojas.

Este módulo se encarga de crear archivos Excel locales que combinan
los datos procesados de Argentina y Andreani en un solo archivo
con múltiples hojas.

Funcionalidades principales:
- Creación de archivos Excel con múltiples hojas
- Detección automática del escritorio (incluye OneDrive)
- Nomenclatura consistente con fechas
- Guardado en el escritorio del usuario

Características:
- Detecta automáticamente carpetas sincronizadas con OneDrive
- Manejo de errores en escritura de archivos
- Compatibilidad con openpyxl para archivos .xlsx
- Nomenclatura descriptiva con fechas

Autor: Sistema de Gestión de Pedidos
"""

import pandas as pd
import os
from datetime import datetime
import FiltroArgentina as fa
import filtroAndreani as fan

def procesar_ambos_archivos(archivo_argentina_procesado, archivo_andreani_procesado, fecha_argentina):
    """
    Crea un archivo Excel unificado con los datos procesados de ambos formatos.
    
    Esta función toma los DataFrames ya procesados por FiltroArgentina y filtroAndreani
    y los guarda en un solo archivo Excel con dos hojas separadas.
    
    Args:
        archivo_argentina_procesado (pandas.DataFrame): Datos procesados para formato Argentina
        archivo_andreani_procesado (pandas.DataFrame): Datos procesados para formato Andreani  
        fecha_argentina (str): Fecha en formato DD-MM-YYYY para nomenclatura del archivo
        
    Returns:
        str: Ruta completa del archivo Excel creado
        
    Proceso:
        1. Detecta la ubicación correcta del escritorio (OneDrive o local)
        2. Genera nombre de archivo con fecha
        3. Crea archivo Excel con dos hojas
        4. Guarda ambos DataFrames sin índices
        5. Maneja errores de escritura
    """
    
    # Intentar detectar la carpeta Desktop sincronizada con OneDrive primero
    desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    
    # Si no existe la carpeta OneDrive/Desktop, usar el escritorio estándar de Windows
    if not os.path.exists(desktop_path):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Crear nombre del archivo Excel con fecha para fácil identificación
    archivo_final_path = os.path.join(desktop_path, f"Archivo_Completo_{fecha_argentina}.xlsx")
    
    try:
        # Usar ExcelWriter para crear archivo con múltiples hojas
        with pd.ExcelWriter(archivo_final_path, engine='openpyxl') as writer:
            # Hoja 1: Datos de Argentina (formato principal)
            archivo_argentina_procesado.to_excel(writer, sheet_name='Argentina', index=False)
            # Hoja 2: Datos de Andreani (formato logístico)
            archivo_andreani_procesado.to_excel(writer, sheet_name='Andreani', index=False)
        
        print(f"Archivo completo guardado correctamente en: {archivo_final_path}")
        
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
    
    return archivo_final_path

def procesar_archivos_unificado(archivo_argentina_procesado, archivo_andreani_procesado, fecha_argentina):
    """
    Función wrapper que mantiene compatibilidad con el código existente.
    
    Esta función simplemente llama a procesar_ambos_archivos con los parámetros correctos.
    Se mantiene para no romper la compatibilidad con el resto del sistema.
    
    Args:
        archivo_argentina_procesado (pandas.DataFrame): Datos procesados para Argentina
        archivo_andreani_procesado (pandas.DataFrame): Datos procesados para Andreani
        fecha_argentina (str): Fecha del archivo
        
    Returns:
        str: Ruta del archivo Excel creado
    """
    return procesar_ambos_archivos(archivo_argentina_procesado, archivo_andreani_procesado, fecha_argentina)