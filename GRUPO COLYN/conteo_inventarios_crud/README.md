# Sistema Sencillo de Conteo Físico de Inventarios con CRUD

Proyecto académico hecho con:

- Python + Flask
- MySQL
- HTML
- CSS
- JavaScript

## ¿Qué hace?

Permite trabajar un CRUD completo de productos:

| Operación | Significado |
|---|---|
| CREATE | Crear productos |
| READ | Consultar productos |
| UPDATE | Actualizar productos |
| DELETE | Eliminar o inactivar productos |

También permite:

1. Registrar conteo físico.
2. Comparar cantidad del sistema vs cantidad física.
3. Calcular automáticamente diferencias.
4. Consultar un reporte de diferencias.

---

## 1. Requisitos

Instalar:

- Python
- MySQL Server
- Visual Studio Code
- Navegador web

---

## 2. Crear la base de datos

Ejecutar en MySQL el archivo:

```text
database/schema.sql
```

---

## 3. Instalar dependencias

Desde la carpeta del proyecto:

```bash
python -m pip install -r requirements.txt
```

---

## 4. Configurar conexión MySQL

Abrir el archivo:

```text
config.py
```

Editar estos datos:

```python
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "conteo_inventarios"
```

---

## 5. Ejecutar el proyecto

```bash
python app.py
```

Abrir en el navegador:

```text
http://127.0.0.1:5000
```

---

## 6. Explicación académica del CRUD

### CREATE - Crear

El usuario llena el formulario de producto y presiona:

```text
Guardar producto
```

El sistema envía la información al backend mediante JavaScript usando `fetch()` y Python guarda el producto en MySQL.

### READ - Consultar

Cuando carga la página, JavaScript consulta:

```text
/api/productos
```

Python obtiene los datos desde MySQL y los muestra en una tabla HTML.

### UPDATE - Actualizar

El usuario presiona:

```text
Editar
```

El sistema carga los datos en el formulario. Luego el usuario modifica y presiona:

```text
Actualizar producto
```

Python actualiza el registro en MySQL.

### DELETE - Eliminar

El usuario presiona:

```text
Eliminar
```

Si el producto no tiene conteos, se elimina.  
Si ya tiene conteos asociados, se cambia su estado a:

```text
Inactivo
```

Esto se hace para no romper la relación con los conteos históricos.

---

## 7. Archivos importantes

```text
app.py                 Backend en Python Flask
templates/index.html   Interfaz HTML
static/css/styles.css  Diseño CSS
static/js/app.js       Lógica JavaScript
database/schema.sql    Base de datos MySQL
config.py              Configuración de conexión
```

---

## 8. Objetivo académico

Este proyecto permite que los aprendices entiendan cómo una aplicación web se conecta con una base de datos para administrar información mediante operaciones CRUD.
