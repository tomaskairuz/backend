CREATE DATABASE sistema;
USE sistema;

CREATE TABLE empleados (
    id INT AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    correo VARCHAR(255) UNIQUE NOT NULL,
    foto VARCHAR(255),
    PRIMARY KEY (id)
);
DESCRIBE empleados;
SELECT * FROM empleados;

DELETE FROM empleados WHERE id<62