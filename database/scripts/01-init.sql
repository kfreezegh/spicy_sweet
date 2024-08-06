-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS spicy_sweet_db;
USE spicy_sweet_db;

-- Crear la tabla usuario
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL -- Se asume que la encriptación se realizará desde la aplicación
);

-- Crear la tabla almacen
CREATE TABLE IF NOT EXISTS almacen (
    id_almacen INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    cantidad INT NOT NULL DEFAULT 0,
    costo FLOAT NOT NULL,
    descripcion VARCHAR(255),
    tipo ENUM('producto', 'ingrediente', 'varios') NOT NULL
);

-- Crear la tabla historial
CREATE TABLE IF NOT EXISTS historial (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_almacen INT NOT NULL,
    fecha DATE NOT NULL,
    tipo ENUM('venta', 'inversion', 'perdida') NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    monto FLOAT NOT NULL,
    FOREIGN KEY (id_almacen) REFERENCES almacen(id_almacen) ON DELETE CASCADE
);

-- Crear el disparador (trigger) para actualizar el campo monto
DELIMITER //

CREATE TRIGGER calcular_monto_historial BEFORE INSERT ON historial
FOR EACH ROW
BEGIN
    DECLARE costo_producto FLOAT;

    -- Obtener el costo del producto desde la tabla almacen
    SELECT costo INTO costo_producto FROM almacen WHERE id_almacen = NEW.id_almacen;

    -- Calcular el monto
    SET NEW.monto = NEW.cantidad * costo_producto;
END;
//

DELIMITER ;

-- Crear la vista vista_productos
CREATE VIEW vista_productos AS
SELECT 
    almacen.nombre AS Nombre, 
    almacen.cantidad AS Existencias, 
    almacen.costo AS Costo, 
    almacen.descripcion AS Descripcion
FROM almacen
WHERE almacen.tipo = 'producto';

-- Crear la vista vista_ingredientes
CREATE VIEW vista_ingredientes AS
SELECT 
    almacen.nombre AS Nombre, 
    almacen.cantidad AS Existencias, 
    almacen.costo AS Costo, 
    almacen.descripcion AS Descripcion
FROM almacen
WHERE almacen.tipo = 'ingrediente';

-- Crear la vista vista_varios
CREATE VIEW vista_varios AS
SELECT 
    almacen.nombre AS Nombre, 
    almacen.cantidad AS Existencias, 
    almacen.costo AS Costo, 
    almacen.descripcion AS Descripcion
FROM almacen
WHERE almacen.tipo = 'varios';

-- Crear la vista vista_venta
CREATE VIEW vista_venta AS
SELECT 
    almacen.nombre AS Nombre, 
    almacen.costo AS Ingreso, 
    historial.fecha AS Fecha
FROM historial
INNER JOIN almacen ON historial.id_almacen = almacen.id_almacen
WHERE historial.tipo = 'venta';

-- Crear la vista vista_inversion
CREATE VIEW vista_inversion AS
SELECT 
    almacen.nombre AS Nombre, 
    almacen.costo AS Egreso, 
    historial.fecha AS Fecha
FROM historial
INNER JOIN almacen ON historial.id_almacen = almacen.id_almacen
WHERE historial.tipo = 'inversion';

-- Crear la vista vista_perdida
CREATE VIEW vista_perdida AS
SELECT 
    almacen.nombre AS Nombre, 
    almacen.costo AS Egreso,
    historial.fecha AS Fecha
FROM historial
INNER JOIN almacen ON historial.id_almacen = almacen.id_almacen
WHERE historial.tipo = 'perdida';
