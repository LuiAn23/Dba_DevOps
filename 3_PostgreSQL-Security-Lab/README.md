# 🛡️ Laboratorio de Seguridad en PostgreSQL: Cifrado y Hashing

Este proyecto demuestra técnicas avanzadas de protección de datos sensibles usando PostgreSQL y pgcrypto, aplicables a sistemas bancarios, de salud o e-commerce.

## 🔍 ¿Qué contiene?
- **Cifrado simétrico** para datos reversibles (CC, números de tarjeta) con `pgp_sym_encrypt/pgp_sym_decrypt`.
- **Hashing irreversible** para contraseñas con `crypt` + `gen_salt`.
- **3 Tablas relacionadas**: `clientes`, `tarjetas`, `credenciales`.
- **Dataset de prueba**: 10 clientes + 20 tarjetas (datos ficticios).

## 🚀 Instalación
1. Clona el repositorio:
   ```bash

   git clone https://github.com/tu-usuario/PostgreSQL-Security-Lab.git

## Ejecuta los scripts en PostgreSQL:

CREATE EXTENSION pgcrypto;
\i scripts/01-create-tables.sql
\i scripts/02-insert-data.sql

🛠️ Tecnologías
PostgreSQL 15+

Extensión pgcrypto

Python (para generación de datos ficticios)

📌 Mejoras futuras
Implementar cifrado asimétrico (claves pública/privada).

Usar funciones de encriptación desde la aplicación (no solo SQL).
