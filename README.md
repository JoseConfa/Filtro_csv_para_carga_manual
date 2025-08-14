# 📊 Sistema de Filtro CSV para Carga Manual

Un sistema avanzado de procesamiento de datos que integra archivos csv con Google Sheets mediante autenticación OAuth2, diseñado para optimizar flujos de trabajo empresariales.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-En%20Desarrollo-yellow)

## 🚀 Características Principales

- ✅ **Autenticación OAuth2** con Google Sheets y Drive
- ✅ **Interfaz gráfica intuitiva** con CustomTkinter
- ✅ **Gestión segura de credenciales** (almacenamiento en %APPDATA%)
- ✅ **Renovación automática de tokens**
- ✅ **Cambio de cuenta sin reiniciar aplicación**
- ✅ **Procesamiento de archivos csv**
- ✅ **Filtros especializados** para Argentina y Andreani
- ✅ **Carga automática a Google Drive**

## 🛠️ Tecnologías Utilizadas

- **Python 3.8+**
- **gspread** - Integración con Google Sheets
- **google-auth** - Autenticación OAuth2
- **tkinter** - Interfaz gráfica
- **pandas** - Procesamiento de datos
- **openpyxl** - Manejo de archivos Excel

## 📋 Requisitos

```bash
pip install gspread google-auth google-auth-oauthlib pandas openpyxl
```

## ⚙️ Configuración

1. **Crear proyecto en Google Cloud Console**
2. **Habilitar APIs de Google Sheets y Drive**
3. **Configurar credenciales OAuth2** en `auth_manager.py`:

```python
"client_id": "tu_client_id_aqui",
"client_secret": "tu_client_secret_aqui"
```

## 📁 Estructura del Proyecto

```
FILTRO_EXCEL_PARA_CARGA_MANUAL/
├── auth_manager.py           # 🔐 Gestor de autenticación OAuth2
├── Main.py                   # 🚀 Aplicación principal
├── Ventana_de_estado.py      # 🖥️ Interfaz gráfica principal
├── FiltroArgentina.py        # 🇦🇷 Filtros específicos para Argentina
├── filtroAndreani.py         # 📦 Filtros para Andreani
├── excel_concat.py           # 📊 Concatenación de archivos Excel
├── Cargar_Drive.py           # ☁️ Carga automática a Google Drive
├── README.md                 # 📖 Documentación
├── LICENSE                   # 📄 Licencia MIT
```

## 🔐 Seguridad y Autenticación

- **OAuth2 Implementation**: Implementación completa del flujo OAuth2 de Google
- **Secure Storage**: Las credenciales se almacenan de forma segura en `%APPDATA%/FiltroExcel/`
- **Auto-refresh**: Tokens de acceso se renuevan automáticamente
- **Account Switching**: Cambio de cuenta sin reiniciar la aplicación

## 📊 Casos de Uso

- **Migración de datos** de Excel a Google Sheets
- **Automatización de reportes** empresariales
- **Sincronización de inventarios**
- **Procesamiento masivo de datos**
- **Integración con servicios de logística** (Andreani)

## 🏗️ Arquitectura

### Componentes Principales

1. **AuthManager**: Manejo completo de autenticación OAuth2
2. **VentanaEstado**: Interfaz gráfica principal con feedback en tiempo real
3. **Filtros Especializados**: Procesamiento específico por región/servicio
4. **Excel Processor**: Manejo avanzado de archivos Excel
5. **Drive Integration**: Carga automática a Google Drive

### Flujo de Trabajo

```
CSV Files → Filtros → Procesamiento → Google Sheets → Google Drive
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**[Jose Confalonieri]** - Desarrollador Python

- 📧 Email: [agustinconfa1997@gmail.com]
- 🐙 GitHub: [@JoseConfa](https://github.com/JoseConfa)

---

## 📊 Estadísticas del Proyecto

- **Líneas de código**: ~2,000+
- **Archivos Python**: 8
- **Dependencias**: 5 principales
- **Tiempo de desarrollo**: 3 meses
- **Versión actual**: 2.0
