CREATE DATABASE IF NOT EXISTS conteo_inventarios;
USE conteo_inventarios;

DROP TABLE IF EXISTS conteos;
DROP TABLE IF EXISTS productos;

CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo_producto VARCHAR(50) NOT NULL UNIQUE,
    nombre_producto VARCHAR(150) NOT NULL,
    categoria VARCHAR(100),
    ubicacion VARCHAR(100),
    stock_sistema INT NOT NULL DEFAULT 0,
    precio_unitario DECIMAL(12,2) DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'Activo'
);

CREATE TABLE conteos (
    id_conteo INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    cantidad_sistema INT NOT NULL,
    cantidad_fisica INT NOT NULL,
    diferencia INT NOT NULL,
    observacion TEXT,
    fecha_conteo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

INSERT INTO productos (
    codigo_producto,
    nombre_producto,
    categoria,
    ubicacion,
    stock_sistema,
    precio_unitario,
    estado
) VALUES
('P001', 'Mouse inalámbrico', 'Tecnología', 'Bodega A', 50, 35000, 'Activo'),
('P002', 'Teclado USB', 'Tecnología', 'Bodega A', 30, 45000, 'Activo'),
('P003', 'Resma de papel carta', 'Papelería', 'Oficina 1', 100, 18000, 'Activo');
