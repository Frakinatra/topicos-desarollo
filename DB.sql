DROP DATABASE login_db;
CREATE DATABASE login_db;

USE login_db;

-- Tabla de usuarios principal
CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
);

-- Tabla de registro de usuarios con datos adicionales
CREATE TABLE user_profiles (
    profile_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,  -- Clave foránea que referencia a la tabla 'users'
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,  -- Validamos que el correo sea único
    password VARCHAR(100) NOT NULL,
    PRIMARY KEY (profile_id),
    FOREIGN KEY (user_id) REFERENCES users(id)  -- Relación con la tabla 'users'
);

INSERT INTO users (username, email, password) VALUES 
('ana_perez', 'ana.perez@example.com', '1234'),
('juan_lopez', 'juan.lopez@example.com', 'password123'),
('maria_gomez', 'maria.gomez@example.com', 'contraseña123'),
('carlos_ruiz', 'carlos.ruiz@example.com', 'pass456'),
('laura_martin', 'laura.martin@example.com', 'laura789'),
('pedro_sanchez', 'pedro.sanchez@example.com', 'pedrito10'),
('sofia_diaz', 'sofia.diaz@example.com', 'sofia2024'),
('david_torres', 'david.torres@example.com', 'davidpass'),
('luis_rojas', 'luis.rojas@example.com', 'luis1234'),
('camila_vega', 'camila.vega@example.com','camipass');
COMMIT;

-- Tabla de proveedores
CREATE TABLE proveedores (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,  -- Nombre del proveedor
    vinculacion VARCHAR(150) NOT NULL,  -- Contacto o área de vinculación
    correo VARCHAR(100) NOT NULL UNIQUE,  -- Correo del proveedor
    telefono VARCHAR(15) NOT NULL,  -- Teléfono del proveedor
    direccion VARCHAR(255) NOT NULL,  -- Dirección del proveedor
    fecha_registro DATE NOT NULL,  -- Fecha de registro del proveedor
    PRIMARY KEY (id)
);

CREATE TABLE carritos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,  -- Relación con la tabla de usuarios
    producto_id INT NOT NULL,  -- Relación con la tabla de productos
    cantidad INT DEFAULT 1,  -- Cantidad de este producto
    FOREIGN KEY (usuario_id) REFERENCES users(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

INSERT INTO proveedores (nombre, vinculacion, correo, telefono, direccion, fecha_registro) VALUES
('Nike', 'Ventas', 'nike@correo.com', '1234567890', 'Av. Principal 123, CDMX, México', '2024-11-30'),
('Adidas', 'Ventas', 'adidas@correo.com', '9876543210', 'Calle Secundaria 456, Monterrey, México', '2024-11-30'),
('Puma', 'Ventas', 'puma@correo.com', '4561237890', 'Boulevard Central 789, Guadalajara, México', '2024-11-30');
COMMIT;

CREATE TABLE categorias (
    id INT NOT NULL AUTO_INCREMENT,
    nombre_categoria VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    PRIMARY KEY (id)
);

INSERT INTO categorias (nombre_categoria, descripcion) VALUES
('Running', 'Calzado diseñado para correr y actividades deportivas.'),
('Casual', 'Tenis para uso diario con diseño cómodo y moderno.'),
('Edición Especial', 'Modelos exclusivos de edición limitada.');
COMMIT;


-- Tabla de productos
CREATE TABLE productos (
    id INT NOT NULL AUTO_INCREMENT,
    proveedor_id INT NOT NULL,  -- Clave foránea que referencia al proveedor
    categoria_id INT NOT NULL,  -- Clave foránea que referencia al catálogo de categorías
    nombre_producto VARCHAR(100) NOT NULL,  -- Nombre del producto
    descripcion TEXT,  -- Descripción del producto
    talla_disponible VARCHAR(20) NOT NULL,  -- Tallas disponibles
    precio DECIMAL(10, 2) NOT NULL,  -- Precio por unidad
    fecha_salida DATE NOT NULL,  -- Fecha de salida del producto
    PRIMARY KEY (id),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE
);


INSERT INTO productos (proveedor_id, categoria_id, nombre_producto, descripcion, talla_disponible, precio, fecha_salida) VALUES
(1, 1, 'Tenis Air Max', 'Tenis de running con diseño ergonómico', '25, 26, 27, 28', 1500.00, '2024-12-01'),
(1, 3, 'Tenis Cortez', 'Edición especial retro de Nike', '25, 26, 27, 28', 2000.00, '2024-12-15'),
(2, 1, 'Tenis Ultraboost', 'Tenis ligeros y cómodos para largas distancias', '24, 25, 26, 27', 1800.00, '2024-11-20'),
(3, 2, 'Tenis Suede Classic', 'Estilo casual icónico de Puma', '23, 24, 25, 26', 1200.00, '2024-12-05');
COMMIT;

SELECT p.nombre_producto, c.nombre_categoria, p.precio
FROM productos p
JOIN categorias c ON p.categoria_id = c.id
WHERE c.nombre_categoria = 'Running';

SELECT 
    p.nombre_producto AS Producto,
    c.nombre_categoria AS Categoría,
    p.precio AS Precio,
    pr.nombre AS Proveedor
FROM 
    productos p
JOIN 
    categorias c ON p.categoria_id = c.id
JOIN 
    proveedores pr ON p.proveedor_id = pr.id
WHERE 
    c.nombre_categoria = 'Running';
