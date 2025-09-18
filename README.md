# Mini Inventario 2
Sistema para control de productos alimenticios desarrollado en Java con CRUD completo y generación de reportes en PDF.
Disponible como ejecutable `.exe` para **Windows** y como paquete `.deb` para distribuciones **Linux** basadas en **Debian** (probado en Ubuntu).

## Tabla de contenido
- [Características principales](#características-principales)
- [Screenshots](#screenshots)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Requerimientos](#requerimientos)
- [Instalación](#instalación)
- [Desarrollo](#desarrollo)
- [Licencia](#licencia)

## Características principales
- CRUD de productos (Crear, Leer, Actualizar, Eliminar).
- Conexión a MariaDB para almacenamiento de datos.
- Interfaz gráfica desarrollada con **PySide6** (Qt).
- Visualización de registros en tabla dinámica.
- Generación de reportes **PDF** con logotipo, fecha actual y listado de productos (ReportLab).

## Screenshots

### Pantalla principal
![pantalla principal](screenshots/Linux/03-seleccionar-producto.png)
> Pantalla principal con datos de prueba

### Pantalla de reportes
![pantalla reportes](screenshots/Linux/06-previsualizar-reporte.png)
> Pantalla de previsualización de reportes

📂 Puedes ver más capturas en la carpeta [/screenshots](screenshots/).

## Tecnologías utilizadas
**Frontend**
- PySide6
- ReportLab

**Backend**
- Python 3.13.7

**Base de datos**
- MariaDB 12.0.2

#### Requerimientos
- [Python 3.13.7](https://download.oracle.com/java/23/archive/jdk-23.0.1_windows-x64_bin.exe)
- [pip](https://pypi.org/project/pip/)
- [MariaDB 12.0.2](https://mariadb.org/download/)

## Instalación

### Windows
#### 1. Crear base de datos
- Copia y ejecuta el [esquema](database/scheme.sql) que se encuentra en el repositorio.
- Crea al usuario para el programa ejecutando la instrucción [seed](database/seed.sql).

#### 2. Instala PySide6 y las librerías necesarias.
```bash
pip install pyside6 mariadb reportlab PyPDF2 pyinstaller
```

#### 3. Descargar el proyecto
- Puedes descargar el ejecutable `.exe` más reciente de Mini Inventario 2 desde [GitHub Releases](https://github.com/mendozarojasdev/mini-inventario-python/releases/latest).
- Puedes colocar el ejecutable `.exe` en una ubicación p. ej. `C:\Program Files\Mini Inventario 2` y crear un acceso directo en el escritorio.

### Linux (Probado en Ubuntu)

#### 1. Crear base de datos
- Copia y ejecuta el [esquema](database/scheme.sql) que se encuentra en el repositorio.
- Crea al usuario para el programa ejecutando la instrucción [seed](database/seed.sql).
Asegúrate de tener instalado las librerías de MariaDB.
```bash
sudo apt install libmariadb-dev
```

#### 2. Instalar librerías de Python
Instala las librerías de Python necesarias con el siguiente comando.
```bash
sudo apt install python3 python3-venv python3-pip
```

#### 3. Descargar el proyecto
Puedes descargar el paquete `.deb` más reciente de Mini Inventario 2 desde [GitHub Releases](https://github.com/mendozarojasdev/mini-inventario-python/releases/latest).

#### 4. Instalar el paquete
- Instala el paquete .deb con el siguiente comando.
```bash
sudo dpkg -i mini_inventario_2.deb
```

✅ Listo, ahora podrás continuar con el desarrollo del proyecto.

## Licencia
Mini Inventario 2 está publicado bajo la licencia MIT. Consulta el archivo [MIT license](https://github.com/mendozarojasdev/mini-inventario-python/blob/master/LICENSE) para más información.
