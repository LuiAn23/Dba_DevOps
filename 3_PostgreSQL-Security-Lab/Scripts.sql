Documentacion del proceso: 


-- Tabla clientes (cifrado simétrico)
CREATE TABLE clientes (
    cliente_id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL,
    cc_encrypted BYTEA NOT NULL
);

-- Tabla tarjetas (cifrado simétrico)
CREATE TABLE tarjetas (
    tarjeta_id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES clientes(cliente_id),
    numero_tarjeta_encrypted BYTEA NOT NULL,
    fecha_vencimiento TEXT NOT NULL
);

-- Tabla credenciales (hash)
CREATE TABLE credenciales (
    credencial_id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES clientes(cliente_id),
    usuario TEXT NOT NULL,
    password_hash TEXT NOT NULL
);


---- Consultar Datos Cifrados
Para descifrar los datos al consultar (solo con la clave correcta):

-- Obtener datos del cliente y su tarjeta (descifrando)
SELECT 
    c.nombre,
    c.email,
    pgp_sym_decrypt(c.cc_encrypted::bytea, 'clave_super_secreta') AS cc_desencriptado,
    pgp_sym_decrypt(t.numero_tarjeta_encrypted::bytea, 'clave_super_secreta') AS tarjeta_desencriptada,
    t.fecha_vencimiento
FROM 
    clientes c
JOIN 
    tarjetas t ON c.cliente_id = t.cliente_id;
	
	


-- Insertar 10 clientes con CC cifrados
INSERT INTO clientes (nombre, email, cc_encrypted) VALUES
    ('Laura Méndez', 'laura.mendez@example.com', pgp_sym_encrypt('1023456789', 'clave_secreta')),
    ('Andrés Ramírez', 'andres.ramirez@example.com', pgp_sym_encrypt('1034567890', 'clave_secreta')),
    ('Sofía Castro', 'sofia.castro@example.com', pgp_sym_encrypt('1045678901', 'clave_secreta')),
    ('Javier Rojas', 'javier.rojas@example.com', pgp_sym_encrypt('1056789012', 'clave_secreta')),
    ('Valentina Díaz', 'valentina.diaz@example.com', pgp_sym_encrypt('1067890123', 'clave_secreta')),
    ('Diego Herrera', 'diego.herrera@example.com', pgp_sym_encrypt('1078901234', 'clave_secreta')),
    ('Camila Gutiérrez', 'camila.gutierrez@example.com', pgp_sym_encrypt('1089012345', 'clave_secreta')),
    ('Ricardo Peña', 'ricardo.pena@example.com', pgp_sym_encrypt('1090123456', 'clave_secreta')),
    ('Isabel Vargas', 'isabel.vargas@example.com', pgp_sym_encrypt('1101234567', 'clave_secreta')),
    ('Gabriel Silva', 'gabriel.silva@example.com', pgp_sym_encrypt('1112345678', 'clave_secreta'));

-- Insertar 20 tarjetas (algunos clientes tienen 1, otros 2 tarjetas)
INSERT INTO tarjetas (cliente_id, numero_tarjeta_encrypted, fecha_vencimiento) VALUES
    -- Cliente 1 (Laura Méndez) - 2 tarjetas
    (1, pgp_sym_encrypt('4532875319641234', 'clave_secreta'), '08/25'),
    (1, pgp_sym_encrypt('5512378934567890', 'clave_secreta'), '11/26'),
    
    -- Cliente 2 (Andrés Ramírez) - 1 tarjeta
    (2, pgp_sym_encrypt('4024007193845309', 'clave_secreta'), '03/24'),
    
    -- Cliente 3 (Sofía Castro) - 2 tarjetas
    (3, pgp_sym_encrypt('5178934561238904', 'clave_secreta'), '05/25'),
    (3, pgp_sym_encrypt('378282246310005', 'clave_secreta'), '09/27'),
    
    -- Cliente 4 (Javier Rojas) - 2 tarjetas
    (4, pgp_sym_encrypt('6011114598723456', 'clave_secreta'), '12/24'),
    (4, pgp_sym_encrypt('5555345678901234', 'clave_secreta'), '04/26'),
    
    -- Cliente 5 (Valentina Díaz) - 1 tarjeta
    (5, pgp_sym_encrypt('4111119876543210', 'clave_secreta'), '07/25'),
    
    -- Cliente 6 (Diego Herrera) - 2 tarjetas
    (6, pgp_sym_encrypt('2223000048410010', 'clave_secreta'), '02/24'),
    (6, pgp_sym_encrypt('5105105105105100', 'clave_secreta'), '10/26'),
    
    -- Cliente 7 (Camila Gutiérrez) - 2 tarjetas
    (7, pgp_sym_encrypt('371449635398431', 'clave_secreta'), '06/25'),
    (7, pgp_sym_encrypt('3566002020360505', 'clave_secreta'), '01/27'),
    
    -- Cliente 8 (Ricardo Peña) - 1 tarjeta
    (8, pgp_sym_encrypt('4001919257537193', 'clave_secreta'), '03/24'),
    
    -- Cliente 9 (Isabel Vargas) - 2 tarjetas
    (9, pgp_sym_encrypt('5555551234567890', 'clave_secreta'), '09/25'),
    (9, pgp_sym_encrypt('6011000990139424', 'clave_secreta'), '12/26'),
    
    -- Cliente 10 (Gabriel Silva) - 3 tarjetas (ejemplo extra)
    (10, pgp_sym_encrypt('4111111111111111', 'clave_secreta'), '08/24'),
    (10, pgp_sym_encrypt('4222222222222', 'clave_secreta'), '05/25'),
    (10, pgp_sym_encrypt('3530111333300000', 'clave_secreta'), '11/27');

commit ;


----- Validación: Verifica que los datos se descifren correctamente:

SELECT cliente_id, pgp_sym_decrypt(cc_encrypted::bytea, 'clave_secreta') AS cc_desencriptado
FROM clientes ;


-- Verificar la contraseña del cliente_id 1 (Laura Méndez)

SELECT c.cliente_id, c.nombre, cr.usuario
FROM clientes c
JOIN credenciales cr ON c.cliente_id = cr.cliente_id
WHERE cr.usuario = 'laura.mendez'
AND cr.password_hash = crypt('password123', cr.password_hash);



------- validar como esta cifrado.

SELECT 
    c.cliente_id,
    c.nombre,
    c.email,
    pgp_sym_decrypt(c.cc_encrypted::bytea, 'clave_secreta') AS cc_desencriptado,
    t.tarjeta_id,
    pgp_sym_decrypt(t.numero_tarjeta_encrypted::bytea, 'clave_secreta') AS tarjeta_desencriptada,
    t.fecha_vencimiento,
    cr.usuario,
    cr.password_hash
FROM 
    clientes c
LEFT JOIN 
    tarjetas t ON c.cliente_id = t.cliente_id
LEFT JOIN 
    credenciales cr ON c.cliente_id = cr.cliente_id
ORDER BY 
    c.cliente_id;
	


---- Quiero descifrar estas columnas:

SELECT c.cliente_id, c.nombre, c.cc_encrypted, t.numero_tarjeta_encrypted, cr.password_hash
FROM 
    clientes c
LEFT JOIN 
    tarjetas t ON c.cliente_id = t.cliente_id
LEFT JOIN 
    credenciales cr ON c.cliente_id = cr.cliente_id
ORDER BY 
    c.cliente_id;



-- Verificación (devuelve true/false)
SELECT password_hash = crypt('password123', password_hash) AS es_valida
FROM credenciales
WHERE usuario = 'laura.mendez';



https://github.com/LuiAn23/Dba_DevOps/blob/main/3_PostgreSQL-Security-Lab/README.md