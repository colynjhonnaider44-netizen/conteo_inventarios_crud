
from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, flash
)
from db import get_connection
from werkzeug.security import check_password_hash
from functools import wraps
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY





# ============================================================
# CRUD DE PRODUCTOS
# ============================================================

@app.route("/api/productos", methods=["GET"])
def listar_productos():
    """
    READ / CONSULTAR:
    Lista todos los productos registrados en la base de datos.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id_producto,
            codigo_producto,
            nombre_producto,
            categoria,
            ubicacion,
            stock_sistema,
            precio_unitario,
            estado
        FROM productos
        ORDER BY id_producto DESC
    """)

    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(productos)


@app.route("/api/productos/<int:id_producto>", methods=["GET"])
def obtener_producto(id_producto):
    """
    READ / CONSULTAR UNO:
    Consulta un solo producto por su ID.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id_producto,
            codigo_producto,
            nombre_producto,
            categoria,
            ubicacion,
            stock_sistema,
            precio_unitario,
            estado
        FROM productos
        WHERE id_producto = %s
    """, (id_producto,))

    producto = cursor.fetchone()

    cursor.close()
    conn.close()

    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify(producto)


@app.route("/api/productos", methods=["POST"])
def crear_producto():
    """
    CREATE / CREAR:
    Registra un nuevo producto.
    """
    data = request.get_json()

    codigo_producto = data.get("codigo_producto")
    nombre_producto = data.get("nombre_producto")
    categoria = data.get("categoria")
    ubicacion = data.get("ubicacion")
    stock_sistema = data.get("stock_sistema")
    precio_unitario = data.get("precio_unitario")

    if not codigo_producto or not nombre_producto:
        return jsonify({"error": "El código y el nombre del producto son obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO productos (
                codigo_producto,
                nombre_producto,
                categoria,
                ubicacion,
                stock_sistema,
                precio_unitario,
                estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'Activo')
        """, (
            codigo_producto,
            nombre_producto,
            categoria,
            ubicacion,
            stock_sistema,
            precio_unitario
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": f"No se pudo registrar el producto: {str(e)}"}), 500

    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Producto registrado correctamente"}), 201


@app.route("/api/productos/<int:id_producto>", methods=["PUT"])
def actualizar_producto(id_producto):
    """
    UPDATE / ACTUALIZAR:
    Actualiza los datos de un producto existente.
    """
    data = request.get_json()

    codigo_producto = data.get("codigo_producto")
    nombre_producto = data.get("nombre_producto")
    categoria = data.get("categoria")
    ubicacion = data.get("ubicacion")
    stock_sistema = data.get("stock_sistema")
    precio_unitario = data.get("precio_unitario")
    estado = data.get("estado", "Activo")

    if not codigo_producto or not nombre_producto:
        return jsonify({"error": "El código y el nombre del producto son obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_producto
        FROM productos
        WHERE id_producto = %s
    """, (id_producto,))

    existe = cursor.fetchone()

    if not existe:
        cursor.close()
        conn.close()
        return jsonify({"error": "Producto no encontrado"}), 404

    try:
        cursor.execute("""
            UPDATE productos
            SET
                codigo_producto = %s,
                nombre_producto = %s,
                categoria = %s,
                ubicacion = %s,
                stock_sistema = %s,
                precio_unitario = %s,
                estado = %s
            WHERE id_producto = %s
        """, (
            codigo_producto,
            nombre_producto,
            categoria,
            ubicacion,
            stock_sistema,
            precio_unitario,
            estado,
            id_producto
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": f"No se pudo actualizar el producto: {str(e)}"}), 500

    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Producto actualizado correctamente"})


@app.route("/api/productos/<int:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    """
    DELETE / ELIMINAR:
    Elimina un producto.

    Nota:
    Si el producto ya tiene conteos registrados, no se puede eliminar
    directamente porque existe una relación con la tabla conteos.
    En ese caso, se cambia su estado a 'Inactivo'.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_producto
        FROM productos
        WHERE id_producto = %s
    """, (id_producto,))

    producto = cursor.fetchone()

    if not producto:
        cursor.close()
        conn.close()
        return jsonify({"error": "Producto no encontrado"}), 404

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM conteos
        WHERE id_producto = %s
    """, (id_producto,))

    conteos = cursor.fetchone()["total"]

    try:
        if conteos > 0:
            cursor.execute("""
                UPDATE productos
                SET estado = 'Inactivo'
                WHERE id_producto = %s
            """, (id_producto,))
            mensaje = "El producto tenía conteos asociados, por eso se dejó como Inactivo."
        else:
            cursor.execute("""
                DELETE FROM productos
                WHERE id_producto = %s
            """, (id_producto,))
            mensaje = "Producto eliminado correctamente."

        conn.commit()

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": f"No se pudo eliminar el producto: {str(e)}"}), 500

    cursor.close()
    conn.close()

    return jsonify({"mensaje": mensaje})


# ============================================================
# CONTEO FÍSICO
# ============================================================

@app.route("/api/conteos", methods=["POST"])
def registrar_conteo():
    """
    Registra un conteo físico de un producto.
    """
    data = request.get_json()

    id_producto = data.get("id_producto")
    cantidad_fisica = data.get("cantidad_fisica")
    observacion = data.get("observacion")

    if not id_producto or cantidad_fisica is None:
        return jsonify({"error": "El producto y la cantidad física son obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT stock_sistema
        FROM productos
        WHERE id_producto = %s
    """, (id_producto,))

    producto = cursor.fetchone()

    if not producto:
        cursor.close()
        conn.close()
        return jsonify({"error": "Producto no encontrado"}), 404

    cantidad_sistema = int(producto["stock_sistema"])
    cantidad_fisica = int(cantidad_fisica)
    diferencia = cantidad_fisica - cantidad_sistema

    cursor.execute("""
        INSERT INTO conteos (
            id_producto,
            cantidad_sistema,
            cantidad_fisica,
            diferencia,
            observacion
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        id_producto,
        cantidad_sistema,
        cantidad_fisica,
        diferencia,
        observacion
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "mensaje": "Conteo registrado correctamente",
        "cantidad_sistema": cantidad_sistema,
        "cantidad_fisica": cantidad_fisica,
        "diferencia": diferencia
    }), 201



app.secret_key = SECRET_KEY

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "id_usuario" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        conexion = None
        cursor = None

        try:
            conexion = get_connection()
            cursor = conexion.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT id_usuario, usuario, password_hash, nombre, activo
                FROM usuarios
                WHERE usuario = %s
                """,
                (usuario,)
            )

            datos = cursor.fetchone()

            if (
                datos
                and datos["activo"] == 1
                and check_password_hash(datos["password_hash"], password)
            ):
                session.clear()
                session["id_usuario"] = datos["id_usuario"]
                session["usuario"] = datos["usuario"]
                session["nombre"] = datos["nombre"] or datos["usuario"]

                return redirect(url_for("inicio"))

            flash("Usuario o contraseña incorrectos, o cuenta inactiva.", "error")

        except Exception:
            app.logger.exception("Error al iniciar sesión")
            flash("Ocurrió un error al iniciar sesión. Revisa la conexión.", "error")

        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def inicio():
    return render_template("index.html")


@app.route("/api/reporte", methods=["GET"])
def reporte_conteos():
    """
    Muestra el reporte de conteos físicos realizados.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.id_conteo,
            p.codigo_producto,
            p.nombre_producto,
            p.categoria,
            p.ubicacion,
            c.cantidad_sistema,
            c.cantidad_fisica,
            c.diferencia,
            c.observacion,
            c.fecha_conteo
        FROM conteos c
        INNER JOIN productos p ON c.id_producto = p.id_producto
        ORDER BY c.id_conteo DESC
    """)

    reporte = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(reporte)


if __name__ == "__main__":
    app.run(debug=True)
