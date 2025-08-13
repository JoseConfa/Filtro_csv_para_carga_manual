"""
Ventana_de_estado.py
====================
Interfaz gráfica principal del sistema Pedidos Manager v2.0.

Este módulo contiene toda la lógica de la interfaz de usuario, incluyendo:
- Interfaz gráfica moderna con CustomTkinter
- Gestión de estados de la aplicación
- Barra de progreso y mensajes en tiempo real
- Dashboard de estadísticas
- Manejo de eventos de usuario
- Integración con módulos de procesamiento

La interfaz está diseñada para ser intuitiva y proporcionar feedback
visual constante durante el procesamiento de pedidos.

Componentes principales:
- Header: Título y botones principales (Cargar archivo, Cambiar cuenta)
- Progress: Barra de progreso con porcentajes y estado actual
- Stats: Panel de estadísticas con categorías de pedidos
- Console: Área de mensajes en tiempo real para feedback

Autor: Sistema de Gestión de Pedidos
"""

import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
import pandas as pd
import FiltroArgentina as f
import excel_concat as ec
from auth_manager import AuthManager

# Configuración global del tema visual
ctk.set_appearance_mode("light")  # Tema claro para mejor legibilidad
ctk.set_default_color_theme("blue")  # Tema azul profesional

class App:
    """
    Clase principal de la aplicación GUI.
    
    Esta clase maneja toda la interfaz de usuario y coordina las interacciones
    entre los diferentes módulos del sistema. Proporciona una interfaz moderna
    y responsiva para el procesamiento de pedidos.
    
    Atributos:
        root: Ventana principal de CustomTkinter
        auth_manager: Gestor de autenticación OAuth2
        progress: Barra de progreso visual
        stats_label: Panel de estadísticas
        text_area: Consola de mensajes
        
    Estados manejados:
        - Iniciando: Configuración inicial
        - Conectando: Autenticación con Google
        - Listo: Esperando archivos del usuario
        - Procesando: Transformando datos
        - Subiendo: Carga a Google Sheets
        - Completado: Proceso exitoso
        - Error: Manejo de excepciones
    """
    
    def __init__(self):
        """
        Inicializa la interfaz gráfica y configura todos los componentes.
        
        El proceso de inicialización incluye:
        1. Creación de la ventana principal
        2. Configuración del gestor de autenticación
        3. Setup del layout responsivo
        4. Creación de todos los componentes visuales
        """
        # Crear ventana principal con configuración específica
        self.root = ctk.CTk()
        self.root.title("Pedidos Manager v2.0")
        self.root.geometry("530x580")
        
        # Inicializar gestor de autenticación con referencia a esta ventana
        self.auth_manager = AuthManager(self)

        # Configurar grid responsivo para layout automático
        self.root.grid_columnconfigure(0, weight=1)  # Columna principal expansible
        self.root.grid_rowconfigure(3, weight=0)     # Estadísticas tamaño fijo
        self.root.grid_rowconfigure(4, weight=1)     # Consola expansible
        
        self._crear_header()
        self._crear_progreso()
        self._crear_estadisticas() 
        self._crear_consola()
    
    def _crear_header(self):
        """
        Crea el header de la aplicación con título y botones principales.
        
        Componentes del header:
        - Título principal "Pedidos Manager"
        - Botón "Cargar archivo" para iniciar procesamiento
        - Botón "Cambiar cuenta" para cambiar cuenta de Google
        """
        # Frame contenedor del header (transparente para integración visual)
        header_frame = ctk.CTkFrame(self.root, corner_radius=15, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))
        
        # Título principal con estilo destacado
        title_label = ctk.CTkLabel(header_frame, 
                                  text="Pedidos Manager", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(10,5))

        # Frame para agrupar los botones horizontalmente
        buttons_frame = ctk.CTkFrame(header_frame, corner_radius=15, fg_color="transparent")
        buttons_frame.pack(pady=(0,10))

        # Botón principal: Cargar archivo (acción primaria)
        self.boton_cargar_archivos = ctk.CTkButton(buttons_frame, 
                                                  text="Cargar archivo",
                                                  font=ctk.CTkFont(weight="bold"),
                                                  width=130,
                                                  height=32,
                                                  command=self.boton_cargar_archivos)
        self.boton_cargar_archivos.pack(side="left", padx=(0,10))

        # Botón secundario: Cambiar cuenta (acción de configuración)
        self.boton_cambiar_cuenta = ctk.CTkButton(buttons_frame, 
                                                 text="Cambiar cuenta",
                                                 font=ctk.CTkFont(weight="bold"),
                                                 width=130,
                                                 height=32,
                                                 fg_color="red",      # Color distintivo para acción crítica
                                                 hover_color="red",
                                                 command=self.cambiar_cuenta_google)
        self.boton_cambiar_cuenta.pack(side="left")
    
    def _crear_progreso(self):
        """
        Crea la sección de progreso con barra visual y estado textual.
        
        Componentes:
        - Label de estado actual
        - Barra de progreso animada
        - Porcentaje numérico
        """
        # Estado actual del sistema
        self.status_label = ctk.CTkLabel(self.root, 
                                        text="ESTADO: Iniciando...", 
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.grid(row=1, column=0, sticky="ew", padx=20, pady=(0,10))
        
        # Frame contenedor del progreso
        progress_frame = ctk.CTkFrame(self.root, corner_radius=15, fg_color="transparent")
        progress_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0,10))
        
        # Barra de progreso visual
        self.progress = ctk.CTkProgressBar(progress_frame, 
                                          width=500, 
                                          height=20, 
                                          corner_radius=10)
        self.progress.pack(pady=10)
        self.progress.set(0)  # Iniciar en 0%
        
        # Indicador numérico de porcentaje
        self.percent_label = ctk.CTkLabel(progress_frame, 
                                         text="0%", 
                                         font=ctk.CTkFont(size=10))
        self.percent_label.pack()
    
    def _crear_estadisticas(self):
        """
        Crea el panel de estadísticas para mostrar resumen de categorías.
        
        El panel muestra:
        - Cantidad de pedidos por categoría
        - Total de pedidos procesados
        - Información actualizada en tiempo real
        """
        # Frame del dashboard con altura fija
        self.stats_frame = ctk.CTkFrame(self.root, corner_radius=15, height=170)
        self.stats_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,5))
        self.stats_frame.grid_propagate(False)  # Mantener altura fija
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_rowconfigure(0, weight=0)

        # Label para mostrar estadísticas con formato tabulado
        self.stats_label = ctk.CTkLabel(self.stats_frame,
                                        height=148, 
                                       text="Estadísticas aparecerán aquí", 
                                       font=ctk.CTkFont(size=12, weight="bold"),
                                       justify="center")
        self.stats_label.pack(pady=15, padx=15, expand=True, fill="both")
    
    def _crear_consola(self):
        """
        Crea la consola de mensajes en tiempo real.
        
        Características:
        - Estilo terminal (fondo negro, texto blanco)
        - Font monoespaciada para mejor legibilidad
        - Auto-scroll a mensajes nuevos
        - Solo lectura para el usuario
        """
        # Frame contenedor de la consola
        text_frame = ctk.CTkFrame(self.root, corner_radius=15, height=150)
        text_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0,10))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        # Área de texto con estilo terminal
        self.text_area = ctk.CTkTextbox(text_frame, 
                                       corner_radius=10,
                                       height=150,
                                       fg_color="black",           # Fondo negro tipo terminal
                                       text_color="white",         # Texto blanco para contraste
                                       font=ctk.CTkFont(family="Consolas", size=11))  # Font monoespaciada
        self.text_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.text_area.configure(state="disabled")  # Solo lectura por defecto

    def cambiar_cuenta_google(self):
        """
        Gestiona el cambio de cuenta de Google para la autenticación.
        
        Este método permite al usuario cambiar de cuenta de Google sin necesidad
        de reiniciar la aplicación. Es útil cuando se necesita usar una cuenta
        diferente o resolver problemas de autenticación.
        
        Proceso:
        1. Solicita confirmación al usuario
        2. Elimina credenciales existentes
        3. Inicia nuevo flujo de autenticación
        4. Actualiza el cliente de Google Sheets
        5. Muestra confirmación de éxito
        
        Maneja errores de autenticación y proporciona feedback visual.
        """
        # Solicitar confirmación antes de proceder (acción irreversible)
        respuesta = messagebox.askyesno(
            "Cambiar cuenta de Google", 
            "¿Estás seguro de que quieres cambiar de cuenta de Google?\n\nSe abrirá tu navegador para seleccionar otra cuenta."
        )
        
        if respuesta:
            try:
                self.actualizar_progreso(10, "Cambiando cuenta de Google...")
                
                # Usar AuthManager para cambio seguro de cuenta
                self.auth_manager.cambiar_cuenta()
                
                # Crear nuevo cliente con las nuevas credenciales
                self.gc = self.auth_manager.crear_cliente_gspread()
                
                self.actualizar_progreso(100, "Cuenta cambiada exitosamente")
                self.agregar_mensaje("Cuenta de Google cambiada exitosamente")
                
                # Confirmar éxito al usuario
                messagebox.showinfo("Éxito", "Cuenta de Google cambiada exitosamente")
            
            except Exception as e:
                # Manejo de errores con feedback claro
                self.mostrar_error(f"Error al cambiar la cuenta: {str(e)}")
                self.actualizar_progreso(0, "Error al cambiar cuenta")

    def actualizar_progreso(self, porcentaje, estado_texto):
        """
        Actualiza la barra de progreso y el estado visual de la aplicación.
        
        Args:
            porcentaje (int): Progreso de 0 a 100
            estado_texto (str): Descripción del estado actual
            
        Esta función asegura que la interfaz refleje el progreso actual del
        procesamiento y proporcione feedback visual constante al usuario.
        """
        try:
            # Validar rango del porcentaje (0-100)
            porcentaje = max(0, min(100, porcentaje))
            
            # Actualizar componentes visuales
            self.progress.set(porcentaje / 100.0)  # Progress bar espera valores 0.0-1.0
            self.status_label.configure(text=f"ESTADO: {estado_texto}")
            self.percent_label.configure(text=f"{porcentaje}%")
            
            # Forzar actualización de la interfaz para mostrar cambios inmediatamente
            self.root.update_idletasks()
            
        except Exception as e:
            # Logging de errores para debugging (no interrumpir flujo principal)
            print(f"Error actualizando progreso: {e}")

    def mostrar_exito(self):
        """
        Muestra mensaje de éxito al usuario.
        
        Utiliza threading safety para mostrar el mensaje desde cualquier hilo.
        """
        self.root.after(0, lambda: messagebox.showinfo(" Éxito", "Pedidos cargados con éxito"))
    
    def mostrar_error(self, mensaje):
        """
        Muestra mensaje de error al usuario.
        
        Args:
            mensaje (str): Descripción del error ocurrido
            
        Utiliza threading safety para mostrar errores desde cualquier hilo.
        """
        self.root.after(0, lambda: messagebox.showerror(" Error", mensaje))
    
    def agregar_mensaje(self, mensaje):
        """
        Agrega un mensaje a la consola en tiempo real.
        
        Args:
            mensaje (str): Mensaje a mostrar en la consola
            
        Características:
        - Auto-scroll a nuevos mensajes
        - Timestamp implícito por orden de llegada
        - Formato de terminal profesional
        """
        # Habilitar edición temporalmente
        self.text_area.configure(state="normal")
        # Agregar mensaje con salto de línea
        self.text_area.insert("end", mensaje + '\n')
        # Auto-scroll al final para mostrar último mensaje
        self.text_area.see("end")
        # Volver a modo solo lectura
        self.text_area.configure(state="disabled")
        # Actualizar inmediatamente
        self.root.update()

    def actualizar_estadisticas(self, caba=0, falta_pagar=0, vencido=0, reembolsado=0, notas=0, sin_clasificar=0, revisar_dni=0):
        """
        Actualiza el panel de estadísticas con los datos procesados.
        
        Args:
            caba (int): Pedidos de CABA
            falta_pagar (int): Pedidos pendientes de pago
            vencido (int): Pedidos vencidos
            reembolsado (int): Pedidos reembolsados
            notas (int): Pedidos con notas para revisar
            sin_clasificar (int): Pedidos sin categoría específica
            revisar_dni (int): Pedidos con DNI inválido
            
        Muestra un resumen tabulado de todas las categorías con totales.
        """
        # Calcular total de pedidos únicos
        total = caba + falta_pagar + vencido + reembolsado + notas + sin_clasificar + revisar_dni
        
        # Formatear texto con alineación para legibilidad
        stats_text = f""" ESTADÍSTICAS

 CABA: {caba}
 Falta Pagar: {falta_pagar}
 Vencido: {vencido}
 Reembolsado: {reembolsado}
 Notas: {notas}
 Sin Clasificar: {sin_clasificar}

 TOTAL: {total}"""

        # Actualizar label de estadísticas
        self.stats_label.configure(text=stats_text)
        self.root.update_idletasks()
    
    def boton_cargar_archivos(self):
        """
        Maneja el proceso completo de carga y procesamiento de archivos CSV.
        
        Este método ejecuta el pipeline principal de procesamiento:
        1. Selección de archivos CSV por el usuario
        2. Carga y concatenación de múltiples archivos
        3. Procesamiento con FiltroArgentina
        4. Procesamiento con filtroAndreani  
        5. Generación de Excel local
        6. Subida a Google Sheets
        7. Confirmación de éxito
        
        Maneja errores en cada etapa y proporciona feedback visual constante.
        """
        # Abrir diálogo de selección de archivos
        archivo_csv = filedialog.askopenfilenames(
            title="Selecciona uno o más archivos CSV",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        
        if archivo_csv:
            try:
                # === ETAPA 1: CARGA DE ARCHIVOS ===
                self.actualizar_progreso(30, "Cargando archivos CSV...")
                self.agregar_mensaje("Cargando y combinando archivos CSV...")
                
                # Cargar múltiples archivos CSV y combinarlos
                dfs = []
                for archivo in archivo_csv:
                    df = pd.read_csv(archivo)
                    dfs.append(df)

                # Concatenar todos los archivos y ordenar por pedido y cliente
                df_concatenado = pd.concat(dfs, ignore_index=True).sort_values(
                    by=['Name', 'Shipping Name'], ascending=[True, False]
                )

                # === ETAPA 2: PROCESAMIENTO FORMATO ARGENTINA ===
                self.actualizar_progreso(50, "Procesando datos de pedidos...")
                self.agregar_mensaje("Aplicando filtros y categorizaciones...")
                
                # Procesar datos con módulo FiltroArgentina
                archivo_argentina_procesado, fecha_argentina = f.procesar_archivo(df_concatenado)

                # === ETAPA 3: PROCESAMIENTO FORMATO ANDREANI ===
                self.actualizar_progreso(65, "Procesando datos de Andreani...")
                self.agregar_mensaje("Procesando datos para Andreani...")
                
                # Procesar datos con módulo filtroAndreani
                archivo_andreani_procesado, fecha_andreani = self.fand.procesar_archivo(df_concatenado)
                
                # === ETAPA 4: GENERACIÓN DE EXCEL LOCAL ===
                self.actualizar_progreso(75, "Guardando archivo Excel en escritorio...")
                self.agregar_mensaje("Creando archivo Excel unificado...")
                
                # Crear archivo Excel unificado en el escritorio
                archivo_excel_path = ec.procesar_archivos_unificado(archivo_argentina_procesado, archivo_andreani_procesado, fecha_argentina)
                self.agregar_mensaje(f"Excel guardado en el escritorio")

                # === ETAPA 5: SUBIDA A GOOGLE SHEETS ===
                self.actualizar_progreso(80, "Subiendo archivos a Google Drive...")
                self.agregar_mensaje("Subiendo archivos a Google Sheets...")
                
                # Subir archivos procesados a Google Sheets
                self.Cargar_Drive.cargar_excel(self.gc, archivo_argentina_procesado, archivo_andreani_procesado)
                
                # === FINALIZACIÓN ===
                self.actualizar_progreso(100, "Proceso completado exitosamente")
                self.agregar_mensaje("Proceso completado con éxito")

                # Mostrar confirmación final al usuario
                messagebox.showinfo("Pedidos Manager v2.0", "Procesamiento exitoso")

            except Exception as e:
                # Manejo centralizado de errores con feedback detallado
                self.mostrar_error(f"Error al cargar los archivos: {str(e)}")
                self.agregar_mensaje(f"Error: {str(e)}")
                self.actualizar_progreso(0, "Error en procesamiento")


# =============================================================================
# INSTANCIACIÓN GLOBAL Y FUNCIONES DE UTILIDAD
# =============================================================================

# Crear instancia global de la aplicación para acceso desde otros módulos
app = App()

# =============================================================================  
# FUNCIONES WRAPPER PARA COMPATIBILIDAD CON MÓDULOS EXTERNOS
# =============================================================================
# Estas funciones permiten que otros módulos interactúen con la interfaz
# sin necesidad de acceso directo a la instancia de la clase

def actualizar_progreso(porcentaje, estado_texto):
    """
    Función wrapper para actualizar progreso desde módulos externos.
    
    Args:
        porcentaje (int): Progreso de 0 a 100
        estado_texto (str): Descripción del estado actual
    """
    app.actualizar_progreso(porcentaje, estado_texto)

def mostrar_exito():
    """
    Función wrapper para mostrar mensaje de éxito desde módulos externos.
    """
    app.mostrar_exito()

def mostrar_error(mensaje):
    """
    Función wrapper para mostrar errores desde módulos externos.
    
    Args:
        mensaje (str): Mensaje de error a mostrar
    """
    app.mostrar_error(mensaje)

def agregar_mensaje(mensaje):
    """
    Función wrapper para agregar mensajes a la consola desde módulos externos.
    
    Args:
        mensaje (str): Mensaje a agregar a la consola
    """
    app.agregar_mensaje(mensaje)

def actualizar_estadisticas(caba=0, falta_pagar=0, vencido=0, reembolsado=0, notas=0, sin_clasificar=0, revisar_dni=0):
    """
    Función wrapper para actualizar estadísticas desde módulos externos.
    
    Args:
        caba (int): Pedidos de CABA
        falta_pagar (int): Pedidos pendientes de pago  
        vencido (int): Pedidos vencidos
        reembolsado (int): Pedidos reembolsados
        notas (int): Pedidos con notas
        sin_clasificar (int): Pedidos sin categoría
        revisar_dni (int): Pedidos con DNI inválido
    """
    app.actualizar_estadisticas(caba, falta_pagar, vencido, reembolsado, notas, sin_clasificar, revisar_dni)