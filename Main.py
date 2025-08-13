"""
Main.py
=======
Archivo principal del sistema Pedidos Manager v2.0.

Este archivo es el punto de entrada de la aplicación que procesa pedidos de Shopify
para generar archivos Excel y subirlos a Google Sheets.

Funcionalidades principales:
- Inicialización de la interfaz gráfica de usuario
- Configuración de la conexión a Google Sheets
- Coordinación entre módulos de procesamiento

Flujo de ejecución:
1. Crea la ventana de la aplicación
2. Establece conexión con Google Sheets
3. Inicia la interfaz de usuario
4. Espera interacción del usuario (cargar archivos)

Autor: Sistema de Gestión de Pedidos
Versión: 2.0
"""

import FiltroArgentina as fa
import Cargar_Drive
import Ventana_de_estado as ve
import filtroAndreani as fand
from auth_manager import AuthManager

# Crear la instancia principal de la aplicación
app = ve.App()

# Inicializar conexión a Google Sheets al inicio de la aplicación
ve.actualizar_progreso(5, "Conectando a Google Sheets...")
try:
    # Crear cliente autorizado para Google Sheets usando el AuthManager
    gc = app.auth_manager.crear_cliente_gspread()
    ve.agregar_mensaje("Conexión exitosa a Google Sheets")
    
    # Almacenar referencias globales para uso posterior en el procesamiento
    ve.app.gc = gc                      # Cliente de Google Sheets
    ve.app.fa = fa                      # Módulo de filtros para Argentina  
    ve.app.fand = fand                  # Módulo de filtros para Andreani
    ve.app.Cargar_Drive = Cargar_Drive  # Módulo de carga a Google Drive
    
    # Actualizar estado de la interfaz
    ve.actualizar_progreso(0, "Presiona 'Cargar archivo' para comenzar")
    ve.agregar_mensaje("Presiona el botón 'Cargar archivo' para seleccionar archivos CSV...")
    
except Exception as e:
    # Manejo de errores en la conexión inicial
    ve.actualizar_progreso(0, "Error de conexión")
    ve.mostrar_error(f"No se pudo conectar a Google Sheets: {str(e)}")

# Iniciar el bucle principal de la interfaz gráfica
ve.app.root.mainloop()
