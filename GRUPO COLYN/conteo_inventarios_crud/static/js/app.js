// Cuando la página carga, se ejecutan estas funciones
document.addEventListener("DOMContentLoaded", function () {
    cargarProductos();
    cargarReporte();
});

// ============================================================
// FORMULARIO DE PRODUCTOS: CREAR Y ACTUALIZAR
// ============================================================

document.getElementById("formProducto").addEventListener("submit", async function (event) {
    event.preventDefault();

    const idProductoEditar = document.getElementById("id_producto_editar").value;

    const producto = {
        codigo_producto: document.getElementById("codigo_producto").value,
        nombre_producto: document.getElementById("nombre_producto").value,
        categoria: document.getElementById("categoria").value,
        ubicacion: document.getElementById("ubicacion").value,
        stock_sistema: document.getElementById("stock_sistema").value,
        precio_unitario: document.getElementById("precio_unitario").value,
        estado: document.getElementById("estado").value
    };

    let url = "/api/productos";
    let metodo = "POST";

    // Si hay un ID en el campo oculto, significa que vamos a actualizar
    if (idProductoEditar) {
        url = `/api/productos/${idProductoEditar}`;
        metodo = "PUT";
    }

    const respuesta = await fetch(url, {
        method: metodo,
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(producto)
    });

    const resultado = await respuesta.json();

    if (respuesta.ok) {
        alert(resultado.mensaje);
        limpiarFormularioProducto();
        cargarProductos();
        cargarReporte();
    } else {
        alert(resultado.error);
    }
});

// ============================================================
// READ: CARGAR PRODUCTOS
// ============================================================

async function cargarProductos() {
    const respuesta = await fetch("/api/productos");
    const productos = await respuesta.json();

    const tabla = document.getElementById("tablaProductos");
    const select = document.getElementById("id_producto");

    tabla.innerHTML = "";
    select.innerHTML = '<option value="">Seleccione un producto</option>';

    productos.forEach(producto => {
        const claseEstado = producto.estado === "Activo" ? "estado-activo" : "estado-inactivo";

        tabla.innerHTML += `
            <tr>
                <td>${producto.codigo_producto}</td>
                <td>${producto.nombre_producto}</td>
                <td>${producto.categoria || ""}</td>
                <td>${producto.ubicacion || ""}</td>
                <td>${producto.stock_sistema}</td>
                <td>$${Number(producto.precio_unitario).toLocaleString()}</td>
                <td class="${claseEstado}">${producto.estado}</td>
                <td>
                    <button class="btn-edit" onclick="editarProducto(${producto.id_producto})">Editar</button>
                    <button class="btn-delete" onclick="eliminarProducto(${producto.id_producto})">Eliminar</button>
                </td>
            </tr>
        `;

        // Solo productos activos se cargan en el conteo físico
        if (producto.estado === "Activo") {
            select.innerHTML += `
                <option value="${producto.id_producto}">
                    ${producto.codigo_producto} - ${producto.nombre_producto}
                </option>
            `;
        }
    });
}

// ============================================================
// UPDATE: CARGAR DATOS EN FORMULARIO PARA EDITAR
// ============================================================

async function editarProducto(idProducto) {
    const respuesta = await fetch(`/api/productos/${idProducto}`);
    const producto = await respuesta.json();

    if (!respuesta.ok) {
        alert(producto.error);
        return;
    }

    document.getElementById("id_producto_editar").value = producto.id_producto;
    document.getElementById("codigo_producto").value = producto.codigo_producto;
    document.getElementById("nombre_producto").value = producto.nombre_producto;
    document.getElementById("categoria").value = producto.categoria || "";
    document.getElementById("ubicacion").value = producto.ubicacion || "";
    document.getElementById("stock_sistema").value = producto.stock_sistema;
    document.getElementById("precio_unitario").value = producto.precio_unitario;
    document.getElementById("estado").value = producto.estado;

    document.getElementById("tituloFormulario").textContent = "Editar producto";
    document.getElementById("btnGuardar").textContent = "Actualizar producto";
    document.getElementById("btnCancelar").style.display = "block";

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

// ============================================================
// DELETE: ELIMINAR PRODUCTO
// ============================================================

async function eliminarProducto(idProducto) {
    const confirmar = confirm("¿Está seguro de eliminar este producto?");

    if (!confirmar) {
        return;
    }

    const respuesta = await fetch(`/api/productos/${idProducto}`, {
        method: "DELETE"
    });

    const resultado = await respuesta.json();

    if (respuesta.ok) {
        alert(resultado.mensaje);
        cargarProductos();
        cargarReporte();
    } else {
        alert(resultado.error);
    }
}

// ============================================================
// LIMPIAR / CANCELAR EDICIÓN
// ============================================================

function cancelarEdicion() {
    limpiarFormularioProducto();
}

function limpiarFormularioProducto() {
    document.getElementById("formProducto").reset();
    document.getElementById("id_producto_editar").value = "";

    document.getElementById("tituloFormulario").textContent = "Registrar producto";
    document.getElementById("btnGuardar").textContent = "Guardar producto";
    document.getElementById("btnCancelar").style.display = "none";
}

// ============================================================
// REGISTRAR CONTEO FÍSICO
// ============================================================

document.getElementById("formConteo").addEventListener("submit", async function (event) {
    event.preventDefault();

    const conteo = {
        id_producto: document.getElementById("id_producto").value,
        cantidad_fisica: document.getElementById("cantidad_fisica").value,
        observacion: document.getElementById("observacion").value
    };

    const respuesta = await fetch("/api/conteos", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(conteo)
    });

    const resultado = await respuesta.json();

    if (respuesta.ok) {
        alert(
            "Conteo guardado correctamente\n" +
            "Sistema: " + resultado.cantidad_sistema + "\n" +
            "Físico: " + resultado.cantidad_fisica + "\n" +
            "Diferencia: " + resultado.diferencia
        );

        document.getElementById("formConteo").reset();
        cargarReporte();
    } else {
        alert(resultado.error);
    }
});

// ============================================================
// REPORTE DE DIFERENCIAS
// ============================================================

async function cargarReporte() {
    const respuesta = await fetch("/api/reporte");
    const reporte = await respuesta.json();

    const tabla = document.getElementById("tablaReporte");
    tabla.innerHTML = "";

    reporte.forEach(item => {
        let claseDiferencia = "diferencia-cero";

        if (item.diferencia < 0) {
            claseDiferencia = "diferencia-negativa";
        } else if (item.diferencia > 0) {
            claseDiferencia = "diferencia-positiva";
        }

        tabla.innerHTML += `
            <tr>
                <td>${formatearFecha(item.fecha_conteo)}</td>
                <td>${item.codigo_producto}</td>
                <td>${item.nombre_producto}</td>
                <td>${item.ubicacion || ""}</td>
                <td>${item.cantidad_sistema}</td>
                <td>${item.cantidad_fisica}</td>
                <td class="${claseDiferencia}">${item.diferencia}</td>
                <td>${item.observacion || ""}</td>
            </tr>
        `;
    });
}

// Formatea la fecha para verla más clara
function formatearFecha(fecha) {
    const date = new Date(fecha);
    return date.toLocaleString();
}


document.getElementById("formUsuario").addEventListener("submit", async (e) => {
    e.preventDefault();

    const mensaje = document.getElementById("mensajeUsuario");
    const password = document.getElementById("nuevo_password").value;
    const confirmar = document.getElementById("nuevo_confirmar").value;

    if (password !== confirmar) {
        mensaje.textContent = "Las contraseñas no coinciden";
        mensaje.style.color = "red";
        return;
    }

    const respuesta = await fetch("/api/usuarios", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            nombre: document.getElementById("nuevo_nombre").value.trim(),
            usuario: document.getElementById("nuevo_usuario").value.trim(),
            password: password
        })
    });

    const datos = await respuesta.json();

    if (respuesta.ok) {
        mensaje.textContent = datos.mensaje;
        mensaje.style.color = "green";
        e.target.reset();
    } else {
        mensaje.textContent = datos.error;
        mensaje.style.color = "red";
    }
});
