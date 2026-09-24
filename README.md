# Plataforma de Gestión de Citas Médicas

API REST desarrollada con **FastAPI** para la gestión de pacientes, médicos, disponibilidades y citas médicas.

El proyecto permite registrar usuarios con rol de paciente o médico, gestionar perfiles, configurar horarios de disponibilidad y realizar reservas de citas con validaciones de seguridad y reglas de negocio.

> Proyecto académico desarrollado para formación SENA — Análisis y Desarrollo de Software (ADSO).

---

## Tecnologías utilizadas

* Python 3.13
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* SQLite
* JWT
* PyJWT
* Argon2
* HTTPBearer
* CORS
* Swagger / OpenAPI

---

## Características principales

### Autenticación

* Registro de usuarios.
* Inicio de sesión mediante JWT.
* Consulta del usuario autenticado.
* Contraseñas almacenadas mediante hash Argon2.
* Expiración de tokens.
* Protección mediante HTTP Bearer.
* Control de acceso según rol.

### Pacientes

* Consulta del perfil propio.
* Actualización de datos personales.
* Consulta de historial de citas.
* Visualización de sus propias citas.
* Cancelación de sus propias citas.

### Médicos

* Consulta del perfil propio.
* Actualización de información profesional.
* Creación de horarios de disponibilidad.
* Actualización de disponibilidades.
* Desactivación lógica de horarios.
* Consulta de agenda de citas.
* Confirmación o cancelación de citas.

### Citas

* Creación de reservas.
* Estado inicial automático: `pendiente`.
* Estados disponibles:

  * `pendiente`
  * `confirmada`
  * `cancelada`

* Validación de fechas y horas.
* Validación de disponibilidad del médico.
* Prevención de citas duplicadas.
* Prevención de conflictos de horario.
* Cancelación lógica de citas.
* Consulta del historial de citas.

---

## Arquitectura del proyecto

El proyecto utiliza una arquitectura modular separando las responsabilidades principales:

```text
app/
├── database/
│   └── connection.py
│
├── dependencies/
│   ├── database_dependency.py
│   └── auth_dependencies.py
│
├── exceptions/
│   └── handlers.py
│
├── middleware/
│   └── headers.py
│
├── models/
│   ├── usuario.py
│   ├── paciente.py
│   ├── medico.py
│   ├── disponibilidad.py
│   └── cita.py
│
├── routes/
│   ├── auth_routes.py
│   ├── usuarios_routes.py
│   ├── pacientes_routes.py
│   ├── medicos_routes.py
│   ├── disponibilidades_routes.py
│   └── citas_routes.py
│
├── schemas/
│   ├── auth.py
│   ├── usuario.py
│   ├── paciente.py
│   ├── medico.py
│   ├── disponibilidad.py
│   └── cita.py
│
├── security/
│   └── security.py
│
├── services/
│   ├── auth_service.py
│   ├── usuario_service.py
│   ├── paciente_service.py
│   ├── medico_service.py
│   ├── disponibilidad_service.py
│   └── cita_service.py
│
└── main.py
```

### Responsabilidades

**Models**

Definen las tablas, relaciones y restricciones de la base de datos mediante SQLAlchemy.

**Schemas**

Definen la estructura y validación de los datos recibidos y enviados por la API mediante Pydantic.

**Routes**

Contienen los endpoints HTTP y controlan el acceso según el usuario autenticado.

**Services**

Contienen las reglas de negocio y las operaciones sobre los datos.

**Security**

Gestiona el hash de contraseñas, generación y validación de tokens JWT y control de autenticación.

**Dependencies**

Proporcionan la conexión a la base de datos y las dependencias de autenticación y autorización.

**Exceptions**

Centralizan el tratamiento de errores de validación, conflictos de integridad y errores internos.

**Middleware**

Agrega información global a las respuestas HTTP de la API.

---

## Modelo de datos

Las principales entidades del sistema son:

```text
Usuario
   │
   ├── Paciente
   │      │
   │      └── Cita
   │
   └── Médico
          │
          ├── Disponibilidad
          │
          └── Cita
```

### Usuario

Contiene la información de autenticación y datos básicos:

* nombre
* apellido
* email
* teléfono
* documento
* contraseña almacenada como hash
* rol
* estado activo

Los roles permitidos son:

```text
paciente
medico
```

### Paciente

Está asociado a un usuario y contiene información adicional como la dirección.

### Médico

Está asociado a un usuario y contiene:

* especialidad
* registro profesional

### Disponibilidad

Representa los horarios disponibles de un médico.

Incluye:

* día de la semana
* hora de inicio
* hora de finalización
* estado activo

Los días utilizan valores de `0` a `6`.

### Cita

Relaciona un paciente con un médico y contiene:

* fecha
* hora
* estado
* fecha de creación
* fecha de actualización

---

## Reglas de negocio de las citas

Las citas cumplen las siguientes reglas:

1. La fecha no puede estar en el pasado.
2. La hora debe encontrarse dentro de la disponibilidad activa del médico.
3. No se permiten dos citas activas para el mismo médico en la misma fecha y hora.
4. Un paciente no puede tener dos citas activas en la misma fecha y hora.
5. Toda nueva cita comienza automáticamente en estado `pendiente`.
6. Una cita `pendiente` puede pasar a `confirmada` o `cancelada`.
7. Una cita `confirmada` puede pasar a `cancelada`.
8. Una cita `cancelada` no puede volver a activarse.
9. La cancelación es lógica y conserva el historial.
10. Un horario desactivado no puede utilizarse para nuevas reservas.

---

## Endpoints

### Autenticación

| Método | Endpoint         | Descripción                   |
| ------ | ---------------- | ----------------------------- |
| POST   | `/auth/registro` | Registrar usuario             |
| POST   | `/auth/login`    | Iniciar sesión                |
| GET    | `/auth/me`       | Consultar usuario autenticado |

### Usuarios

| Método | Endpoint       | Descripción              |
| ------ | -------------- | ------------------------ |
| GET    | `/usuarios/me` | Consultar perfil propio  |
| PUT    | `/usuarios/me` | Actualizar perfil propio |

### Pacientes

| Método | Endpoint        | Descripción                    |
| ------ | --------------- | ------------------------------ |
| GET    | `/pacientes/me` | Consultar perfil del paciente  |
| PUT    | `/pacientes/me` | Actualizar perfil del paciente |

### Médicos

| Método | Endpoint      | Descripción                  |
| ------ | ------------- | ---------------------------- |
| GET    | `/medicos/me` | Consultar perfil del médico  |
| PUT    | `/medicos/me` | Actualizar perfil del médico |

### Disponibilidades

| Método | Endpoint                 | Descripción                |
| ------ | ------------------------ | -------------------------- |
| GET    | `/disponibilidades`      | Consultar disponibilidades |
| POST   | `/disponibilidades`      | Crear disponibilidad       |
| GET    | `/disponibilidades/{id}` | Consultar disponibilidad   |
| PUT    | `/disponibilidades/{id}` | Actualizar disponibilidad  |
| DELETE | `/disponibilidades/{id}` | Desactivar disponibilidad  |

### Citas

| Método | Endpoint           | Descripción                 |
| ------ | ------------------ | --------------------------- |
| POST   | `/citas`           | Crear cita                  |
| GET    | `/citas/mis-citas` | Consultar citas propias     |
| GET    | `/citas/agenda`    | Consultar agenda del médico |
| GET    | `/citas/{id}`      | Consultar una cita          |
| PUT    | `/citas/{id}`      | Actualizar estado           |
| DELETE | `/citas/{id}`      | Cancelar cita               |

---

## Autenticación y autorización

La API utiliza **JWT** para autenticar a los usuarios.

Después del inicio de sesión se obtiene un token que debe enviarse en las solicitudes protegidas mediante:

```text
Authorization: Bearer <token>
```

Las operaciones están protegidas según el rol:

### Paciente

Puede:

* consultar su perfil
* actualizar su perfil
* crear citas
* consultar sus citas
* consultar el detalle de sus citas
* cancelar sus propias citas

### Médico

Puede:

* consultar su perfil
* actualizar su perfil
* gestionar sus disponibilidades
* consultar su agenda
* consultar sus citas
* confirmar citas
* cancelar citas

---

## Validaciones

La API implementa validaciones mediante Pydantic.

Entre ellas:

* formato de correo electrónico
* formato de teléfono
* documento obligatorio
* contraseñas seguras
* roles válidos
* fechas válidas
* horas válidas
* días de disponibilidad entre `0` y `6`
* hora inicial menor que hora final
* identificadores positivos
* campos no permitidos rechazados
* información profesional obligatoria para médicos

---

## Manejo de errores

La API utiliza respuestas HTTP diferenciadas:

| Código | Significado                         |
| ------ | ----------------------------------- |
| 200    | Operación exitosa                   |
| 201    | Recurso creado                      |
| 400    | Solicitud incorrecta                |
| 401    | No autenticado / token inválido     |
| 403    | Sin permisos                        |
| 404    | Recurso no encontrado               |
| 409    | Conflicto con información existente |
| 422    | Error de validación                 |
| 500    | Error interno del servidor          |

Los errores se gestionan mediante handlers globales para mantener respuestas consistentes.

---

## Base de datos y Alembic

La aplicación utiliza SQLite como base de datos local.

Archivo utilizado durante la ejecución:

```text
citas.db
```

Este archivo se encuentra excluido del repositorio mediante `.gitignore`.

Las modificaciones de la estructura de la base de datos se gestionan mediante Alembic.

### Aplicar migraciones

```powershell
alembic upgrade head
```

### Verificar la migración actual

```powershell
alembic current
```

### Verificar si existen cambios pendientes

```powershell
alembic check
```

La migración actual corresponde al head:

```text
9b7483b4bfaa
```

---

## Instalación

### 1. Clonar o descargar el proyecto

Ubicarse en la carpeta raíz del proyecto:

```text
Proyecto_Final
```

### 2. Crear el entorno virtual

```powershell
python -m venv venv
```

### 3. Activar el entorno virtual

En PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crear un archivo:

```text
.env
```

con una clave secreta para JWT:

```env
SECRET_KEY=REEMPLAZAR_POR_UNA_CLAVE_SECRETA_SEGURA
```

El archivo `.env` no debe subirse al repositorio.

### 6. Aplicar migraciones

```powershell
alembic upgrade head
```

### 7. Ejecutar la API

```powershell
uvicorn app.main:app --reload
```

---

## Documentación de la API

Con el servidor ejecutándose, FastAPI proporciona documentación interactiva mediante Swagger:

```text
http://127.0.0.1:8000/docs
```

También está disponible ReDoc:

```text
http://127.0.0.1:8000/redoc
```

Y el esquema OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

La API utiliza OpenAPI 3.1.0.

---

## CORS

La aplicación incorpora configuración CORS para permitir solicitudes desde clientes autorizados.

Durante las pruebas se verificó correctamente el encabezado:

```text
Access-Control-Allow-Origin
```

---

## Middleware

La API incorpora encabezados personalizados para identificar la aplicación y la versión:

```text
X-App-Name: Plataforma de Citas
X-API-Version: 1.0.0
```

---

## Pruebas realizadas

Se realizó una batería de pruebas funcionales y de seguridad sobre la API.

### Resultado final

```text
Pruebas ejecutadas: 85
Pruebas aprobadas: 85
Pruebas fallidas definitivas: 0
```

Durante el proceso de pruebas se detectaron y corrigieron dos situaciones:

1. El handler global de validaciones generaba un error 500 al intentar serializar determinados errores de Pydantic. Se corrigió la serialización de los detalles de validación para retornar correctamente `422`.

2. Las restricciones iniciales de citas impedían reutilizar determinados horarios después de una cancelación. Se reemplazaron por índices únicos parciales para que las citas canceladas no bloqueen nuevamente el horario.

También se verificaron:

* autenticación JWT
* autorización por roles
* validaciones Pydantic
* disponibilidad médica
* prevención de citas duplicadas
* cancelación lógica
* reutilización de horarios cancelados
* CORS
* middleware
* documentación OpenAPI
* esquema HTTPBearer
* manejo global de errores

---

## Seguridad

El proyecto implementa las siguientes medidas:

* Contraseñas almacenadas mediante Argon2.
* Autenticación mediante JWT.
* Tokens con tiempo de expiración.
* Protección mediante HTTPBearer.
* Autorización basada en roles.
* Variables sensibles mediante `.env`.
* `.env` excluido de Git.
* Base de datos local excluida de Git.
* Entorno virtual excluido de Git.
* Validación estricta de datos mediante Pydantic.

---

## Archivos excluidos del repositorio

El archivo `.gitignore` evita subir información local o sensible:

```text
venv/
.venv/
__pycache__/
.env
.env.*
*.db
*.sqlite
*.sqlite3
.vscode/
.idea/
*.log
.DS_Store
Thumbs.db
```

---

## Estado del proyecto

**Estado:** Finalizado

La API cuenta con:

* autenticación
* autorización por roles
* gestión de pacientes
* gestión de médicos
* gestión de disponibilidades
* gestión de citas
* validaciones
* manejo de errores
* migraciones Alembic
* CORS
* middleware
* documentación Swagger/OpenAPI
* pruebas funcionales y de seguridad

---

## Instalación del proyecto paso a paso 

Esta sección explica cómo instalar y ejecutar el proyecto en un computador diferente al equipo donde fue desarrollado.

### Requisitos previos

Antes de comenzar, el nuevo computador debe tener instalado:

* Windows 10 o Windows 11.
* Python 3.13.
* Git, si el proyecto será descargado desde GitHub.
* PowerShell.

Se recomienda verificar las instalaciones antes de continuar.

### 1. Verificar Python

Abrir **PowerShell** y ejecutar:

```powershell
python --version
```

La versión esperada es:

```text
Python 3.13.x
```

También puede verificarse con:

```powershell
py --version
```

Si Python no está instalado, debe instalarse antes de continuar.

Durante la instalación de Python en Windows se recomienda activar la opción:

```text
Add Python to PATH
```

Después de instalarlo, cerrar y volver a abrir PowerShell.

---

### 2. Verificar Git

Si el proyecto se encuentra en un repositorio Git, verificar que Git esté instalado:

```powershell
git --version
```

Debe aparecer una versión de Git, por ejemplo:

```text
git version 2.x.x
```

Si Git no está instalado, debe instalarse antes de continuar.

---

### 3. Obtener el proyecto

Existen dos formas de obtener el proyecto.

#### Opción A — Clonar desde GitHub

Si el proyecto fue publicado en GitHub, utilizar:

```powershell
git clone URL_DEL_REPOSITORIO
```

Después entrar en la carpeta:

```powershell
cd NOMBRE_DEL_REPOSITORIO
```

Por ejemplo:

```powershell
cd Proyecto_Final
```

#### Opción B — Copiar el proyecto manualmente

Si el proyecto se entrega como una carpeta o archivo `.zip`:

1. Copiar el proyecto al computador.
2. Extraer el archivo `.zip`, si corresponde.
3. Abrir PowerShell.
4. Entrar en la carpeta raíz del proyecto.

Ejemplo:

```powershell
cd "C:\Users\Usuario\Desktop\Proyecto_Final"
```

La carpeta raíz debe contener archivos y carpetas similares a:

```text
Proyecto_Final/
├── alembic/
├── app/
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

No es necesario copiar las siguientes carpetas o archivos desde el computador original:

```text
venv/
.env
citas.db
__pycache__/
```

Estos elementos son locales y/o se generan nuevamente en el nuevo computador.

---

### 4. Abrir PowerShell en la carpeta del proyecto

Comprobar que se está ubicado en la carpeta raíz:

```powershell
Get-ChildItem
```

Deben aparecer elementos como:

```text
alembic
app
.gitignore
alembic.ini
requirements.txt
README.md
```

---

### 5. Crear el entorno virtual

El entorno virtual debe crearse nuevamente en el nuevo computador.

Ejecutar:

```powershell
python -m venv venv
```

Este comando crea una carpeta:

```text
venv/
```

La carpeta contiene un entorno independiente para las dependencias de Python.

---

### 6. Activar el entorno virtual

En PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Si se activa correctamente, el inicio de la terminal mostrará algo similar a:

```text
(venv) PS C:\Users\Usuario\Desktop\Proyecto_Final>
```

---

### 7. Solucionar el bloqueo de scripts de PowerShell

En algunos computadores Windows puede aparecer un mensaje indicando que la ejecución de scripts está deshabilitada.

Si ocurre, ejecutar:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Cuando PowerShell solicite confirmación, seleccionar:

```text
Y
```

Después volver a activar el entorno:

```powershell
.\venv\Scripts\Activate.ps1
```
---

### 8. Actualizar pip

Con el entorno virtual activo:

```powershell
python -m pip install --upgrade pip
```

Comprobar:

```powershell
pip --version
```

---

### 9. Instalar las dependencias

El proyecto contiene el archivo:

```text
requirements.txt
```

Este archivo contiene las dependencias necesarias para ejecutar la API.

Instalarlas con:

```powershell
pip install -r requirements.txt
```

Este proceso puede tardar unos minutos.

Para verificar las dependencias instaladas:

```powershell
pip list
```

---

### 10. Crear el archivo `.env`

El archivo `.env` contiene variables de configuración que no deben almacenarse en el repositorio.

En el nuevo computador debe crearse manualmente.

Desde la raíz del proyecto:

```powershell
New-Item .env -ItemType File
```

Abrirlo:

```powershell
notepad .env
```

Agregar:

```env
SECRET_KEY=REEMPLAZAR_POR_UNA_CLAVE_SECRETA_SEGURA
```

Guardar y cerrar.

### Importante

No utilizar una clave secreta publicada en GitHub o en documentación.

Para generar una clave aleatoria segura se puede utilizar Python:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

El resultado puede copiarse en `.env`:

```env
SECRET_KEY=CLAVE_GENERADA_AQUI
```

Por ejemplo:

```env
SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

La clave mostrada anteriormente es únicamente un ejemplo. Cada instalación debe utilizar su propia clave.

---

### 11. Verificar que `.env` esté protegido

Ejecutar:

```powershell
git status
```

El archivo `.env` **no debe aparecer como archivo para subir**.

Esto se debe a que `.gitignore` contiene:

```text
.env
.env.*
```

Nunca se debe ejecutar:

```powershell
git add .env
```

ni subir manualmente este archivo al repositorio.

---

### 12. Configurar la base de datos

El proyecto utiliza:

```text
SQLite
```

La base de datos local se encuentra en:

```text
citas.db
```

Este archivo no necesita copiarse desde el computador original.

La base de datos debe generarse mediante las migraciones de Alembic.

---

### 13. Ejecutar las migraciones

Con el entorno virtual activo y ubicados en la raíz del proyecto:

```powershell
alembic upgrade head
```

Este comando ejecuta todas las migraciones existentes y crea la estructura necesaria de la base de datos.

Después de ejecutarlo aparecerá el archivo:

```text
citas.db
```

Comprobar:

```powershell
Get-ChildItem citas.db
```

---

### 14. Verificar el estado de Alembic

Ejecutar:

```powershell
alembic current
```

La migración actual debe corresponder al último `head` disponible.

También se puede comprobar si existen cambios pendientes:

```powershell
alembic check
```

Cuando todo está actualizado debe aparecer:

```text
No new upgrade operations detected.
```

---

### 15. Ejecutar la aplicación

Con el entorno virtual activo:

```powershell
uvicorn app.main:app --reload
```

Si la aplicación inicia correctamente, aparecerá un mensaje similar a:

```text
Uvicorn running on http://127.0.0.1:8000
```

No cerrar esta terminal mientras se esté utilizando la API.

---

### 16. Abrir la documentación Swagger

Con la aplicación ejecutándose, abrir un navegador y entrar en:

```text
http://127.0.0.1:8000/docs
```

Swagger permite:

* consultar los endpoints
* revisar los esquemas
* realizar pruebas
* autenticarse mediante Bearer Token
* consultar las respuestas de la API

---

### 17. Abrir ReDoc

También se puede consultar la documentación mediante ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

### 18. Consultar OpenAPI

El esquema OpenAPI está disponible en:

```text
http://127.0.0.1:8000/openapi.json
```

---

## Proceso completo resumido

Para una instalación desde cero en un computador Windows, el flujo principal es:

```powershell
# 1. Obtener el proyecto
git clone URL_DEL_REPOSITORIO

# 2. Entrar al proyecto
cd Proyecto_Final

# 3. Crear entorno virtual
python -m venv venv

# 4. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 5. Actualizar pip
python -m pip install --upgrade pip

# 6. Instalar dependencias
pip install -r requirements.txt

# 7. Crear archivo de variables de entorno
New-Item .env -ItemType File

# 8. Editar variables de entorno
notepad .env

# 9. Crear/actualizar base de datos
alembic upgrade head

# 10. Verificar migraciones
alembic current
alembic check

# 11. Ejecutar API
uvicorn app.main:app --reload
```

Después de iniciar la aplicación:

```text
Swagger:
http://127.0.0.1:8000/docs

ReDoc:
http://127.0.0.1:8000/redoc

OpenAPI:
http://127.0.0.1:8000/openapi.json
```

---

## Solución de problemas comunes

### `python` no se reconoce como comando

Si aparece un mensaje similar a:

```text
python : The term 'python' is not recognized...
```

Python no está disponible en el PATH.

Verificar:

```powershell
py --version
```

Si `py` funciona, se puede crear el entorno mediante:

```powershell
py -3.13 -m venv venv
```

Después:

```powershell
.\venv\Scripts\Activate.ps1
```

---

### No se puede activar `venv`

Si PowerShell indica que no permite ejecutar scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Después:

```powershell
.\venv\Scripts\Activate.ps1
```

---

### `pip install -r requirements.txt` genera errores

Primero comprobar que el entorno virtual está activo:

```powershell
python --version
pip --version
```

El comando debe apuntar al entorno `venv`.

Después actualizar pip:

```powershell
python -m pip install --upgrade pip
```

Y repetir:

```powershell
pip install -r requirements.txt
```

---

### `alembic upgrade head` genera un error

Verificar que:

1. El entorno virtual esté activo.
2. Se esté ejecutando el comando desde la raíz del proyecto.
3. Existan `alembic.ini` y la carpeta `alembic`.
4. Las dependencias estén instaladas.

Comprobar:

```powershell
Get-ChildItem
```

Debe aparecer:

```text
alembic
alembic.ini
app
requirements.txt
```

---

### La API no inicia

Comprobar primero:

```powershell
python -c "import app.main; print('Aplicación importada correctamente')"
```

Si no aparece ningún error, intentar:

```powershell
uvicorn app.main:app --reload
```

---

### El puerto 8000 está ocupado

Si otro programa está utilizando el puerto 8000, ejecutar la API en otro puerto:

```powershell
uvicorn app.main:app --reload --port 8001
```

La documentación estará entonces en:

```text
http://127.0.0.1:8001/docs
```

---

### Se desea detener la API

En la terminal donde está ejecutándose Uvicorn, presionar:

```text
Ctrl + C
```

---

### Se desea volver a iniciar el proyecto posteriormente

No es necesario crear nuevamente el entorno virtual ni instalar las dependencias.

Abrir PowerShell y entrar al proyecto:

```powershell
cd "RUTA_DEL_PROYECTO"
```

Activar el entorno:

```powershell
.\venv\Scripts\Activate.ps1
```

Ejecutar:

```powershell
uvicorn app.main:app --reload
```

---

## Importante sobre archivos locales

Los siguientes archivos o carpetas son específicos de cada computador y no deben copiarse obligatoriamente entre instalaciones:

```text
venv/
.env
citas.db
__pycache__/
```

El nuevo computador debe generar su propio:

```text
venv/
.env
citas.db
```

La estructura de la base de datos se obtiene mediante:

```powershell
alembic upgrade head
```

---

## Seguridad para una nueva instalación

Cada computador o entorno debe utilizar su propia variable:

```env
SECRET_KEY=...
```

No publicar:

* claves secretas
* contraseñas
* tokens JWT
* archivos `.env`
* bases de datos que contengan información real
* credenciales personales

El archivo `.gitignore` está configurado para evitar que estos archivos sean agregados accidentalmente al repositorio.

---

## Para migraciones nuevas

alembic revision --autogenerate -m "descripcion_del_cambio"

alembic revision --autogenerate -m "agregar_campo_telefono"

alembic upgrade head

alembic current