"""
auth_manager.py
===============
Gestor de autenticación OAuth2 para Google Sheets y Google Drive.

Este módulo maneja toda la autenticación y autorización necesaria para acceder
a los servicios de Google. Proporciona funcionalidades para:
- Autenticación OAuth2 con Google
- Gestión de tokens de acceso y refresh tokens  
- Cambio de cuentas de Google
- Creación de clientes autorizados para gspread

Características:
- Almacena credenciales de forma segura en %APPDATA%
- Maneja la renovación automática de tokens
- Permite cambio de cuenta sin reiniciar la aplicación
- Integración con la interfaz gráfica para mostrar estado

Dependencias:
- gspread: Para trabajar con Google Sheets
- google-auth: Para autenticación OAuth2
- google-auth-oauthlib: Para el flujo de autorización

Autor: Sistema de Gestión de Pedidos
"""

import gspread  # Para trabajar con Google Sheets
import os       # Para manejar rutas de archivos
import pickle   # Para guardar/cargar el token del usuario
from google.auth.transport.requests import Request  # Para refrescar tokens
from google.oauth2.credentials import Credentials   # Para manejar credenciales OAuth
from google_auth_oauthlib.flow import InstalledAppFlow  # Para el flujo de autenticación

class AuthManager:
    """
    Gestor de autenticación OAuth2 para servicios de Google.
    
    Esta clase maneja todo el proceso de autenticación, desde la obtención inicial
    de credenciales hasta la renovación de tokens y el cambio de cuentas.
    
    Atributos:
        ventana: Referencia a la ventana principal para mostrar mensajes
        client_config: Configuración del cliente OAuth2
        scopes: Permisos solicitados a Google (Sheets y Drive)
        token_file: Ruta donde se almacenan las credenciales
    """
    
    def __init__(self, ventana=None):
        """
        Inicializa el gestor de autenticación.
        
        Args:
            ventana: Instancia de la ventana principal para mostrar mensajes
        """
        self.ventana = ventana

        # Configuración del cliente OAuth2 - ESTAS CREDENCIALES SON ESPECÍFICAS DEL PROYECTO
        self.client_config = {
            "installed": {
            "client_id": "Tu client id de Google Console aqui",
            "client_secret": "Tu client secret de Google Console aqui",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
        }

        # Permisos requeridos: lectura/escritura de Sheets y creación de archivos en Drive
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]

        # Crear directorio seguro para almacenar el token en %APPDATA%
        app_data = os.getenv('APPDATA')
        token_dir = os.path.join(app_data, 'FiltroExcel')
        os.makedirs(token_dir, exist_ok=True)
        self.token_file = os.path.join(token_dir, "token.pickle")
    
    def eliminar_credenciales(self):
        """
        Elimina las credenciales almacenadas para forzar un nuevo login.
        
        Útil cuando se necesita cambiar de cuenta o resolver problemas de autenticación.
        """
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            if self.ventana:
                self.ventana.agregar_mensaje("Credenciales eliminadas. Se requerirá nuevo login.")
    
    def cambiar_cuenta(self):
        """
        Fuerza un cambio de cuenta eliminando credenciales y solicitando nuevas.
        
        Returns:
            Credentials: Nuevas credenciales del usuario seleccionado
        """
        self.eliminar_credenciales()
        if self.ventana:
            pass  # Mensaje ya mostrado en eliminar_credenciales
        return self.obtener_credenciales(forzar_nuevo_login=True)

    def obtener_credenciales(self, forzar_nuevo_login=False):
        """
        Obtiene o renueva las credenciales OAuth2.
        
        Este método implementa la lógica completa de autenticación:
        1. Intenta cargar credenciales existentes
        2. Verifica si son válidas o necesitan renovación
        3. Si es necesario, inicia el flujo OAuth2 completo
        
        Args:
            forzar_nuevo_login (bool): Si True, ignora credenciales existentes
            
        Returns:
            Credentials: Credenciales válidas para usar con gspread
        """
        credenciales = None

        # Si no se fuerza nuevo login, intentar cargar credenciales existentes
        if not forzar_nuevo_login and os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                credenciales = pickle.load(token)

        # Validar y renovar credenciales si es necesario
        if not credenciales or not credenciales.valid or forzar_nuevo_login:
            if credenciales and credenciales.expired and credenciales.refresh_token and not forzar_nuevo_login:
                # Renovar token automáticamente
                if self.ventana:
                    self.ventana.agregar_mensaje("Renovando credenciales...")
                credenciales.refresh(Request())
            else:
                # Flujo completo de autenticación OAuth2
                flow = InstalledAppFlow.from_client_config(self.client_config, self.scopes)
                flow.redirect_uri = 'http://localhost:8080'
                
                # Configurar parámetros adicionales para obtener id_token
                flow.oauth2session.scope = self.scopes

                # Mostrar información al usuario sobre el proceso de autenticación
                if self.ventana:
                    if forzar_nuevo_login:
                        self.ventana.agregar_mensaje("Cambiando de cuenta de Google...")
                    else:
                        self.ventana.agregar_mensaje("Iniciando autenticación...")
                    self.ventana.agregar_mensaje("Se abrirá tu navegador...")

                # Ejecutar el flujo OAuth (prompt='consent' fuerza la selección de cuenta)
                credenciales = flow.run_local_server(
                    port=8080, 
                    prompt='consent', 
                    open_browser=True
                )

                # Guardar las credenciales para sesiones futuras
                if self.ventana:
                    self.ventana.agregar_mensaje("Autenticación exitosa!")
                with open(self.token_file, 'wb') as token:
                    pickle.dump(credenciales, token)

        return credenciales

    def crear_cliente_gspread(self):
        """
        Crea un cliente autorizado de gspread para trabajar con Google Sheets.
        
        Returns:
            gspread.Client: Cliente autorizado listo para usar
        """
        credenciales = self.obtener_credenciales()
        return gspread.authorize(credenciales)