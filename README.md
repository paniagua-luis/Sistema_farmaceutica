# Sistema de Control de una Farmaceutica

Backend REST para administrar medicamentos, lotes, inspecciones, despachos,
temperaturas, trazabilidad, reportes y usuarios. Esta documentacion compara la
implementacion actual con el documento `Proyecto final (1).pdf` y destaca los
cambios posteriores incorporados al backend.

> **Alcance del repositorio:** el proyecto disponible aqui contiene el backend
> FastAPI y scripts de datos de prueba. El PDF describe tambien un frontend
> React, pero no hay una carpeta ni codigo de frontend en este repositorio.
> Por tanto, los nuevos formatos de recepcion y despacho requieren que la
> interfaz que consume la API se adapte por separado.

## 1. Resumen ejecutivo

La solucion conserva la arquitectura limpia descrita en el proyecto anterior:

```text
app/
  domain/        Entidades y contratos de repositorios
  application/   Casos de uso y reglas de negocio
  infrastructure/ Modelos SQLAlchemy, repositorios, conexion y seguridad
  presentation/  Routers FastAPI, esquemas Pydantic y dependencias
  main.py        Inicializacion de la API, tablas y datos de autorizacion
scripts/
  factories.py   Datos de prueba
  seed.py        Carga idempotente de datos de prueba
```

La API interactua con una base relacional, acepta y devuelve JSON, valida
entradas con Pydantic y publica la documentacion OpenAPI/Swagger.

## 2. Requisitos del proyecto y estado actual

El PDF define doce requisitos funcionales (RF-01 a RF-12), nueve no funcionales
(RNF-01 a RNF-09) y siete subsistemas de comportamiento. El estado siguiente se
refiere al **backend de este repositorio**, no a todas las capturas o pantallas
descritas en el PDF.

| Requisito del proyecto | Estado observado en el backend |
|---|---|
| RF-01 Recepcion de lotes | Implementado. Se registran lotes con proveedor, sucursal, fechas y productos. |
| RF-02 Inspeccion de calidad | Implementado. Se registran resultados aprobado/rechazado y se actualiza el estado del lote. |
| RF-03 Abastecimiento y validacion de stock | Parcial. Se valida y descuenta stock al despachar; no hay una entidad independiente de solicitud de abastecimiento. |
| RF-04 Despacho y confirmacion | Implementado. Hay despacho individual y despacho de varias lineas hacia una sucursal; cada linea produce un despacho. |
| RF-05 Cadena de frio | Parcial. Se registran lecturas y estado; el router actual usa limites generales `-100` y `100`, no los rangos configurados por medicamento. |
| RF-06 Vencimientos y bajas | Parcial. Hay alertas consultadas por API y actualizacion de estado; no hay envio programado, correo ni flujo especializado de autorizacion de bajas. |
| RF-07 Trazabilidad por lote | Implementado mediante historial de eventos por lote. |
| RF-08 Reportes de inventario y regulatorios | Parcial. Hay consultas de inventario y almacenamiento/listado de reportes; no se encontro generacion programada automatica. |
| RF-09 Ficha tecnica de medicamentos | Implementado: alta, consulta, edicion y eliminacion; incluye temperaturas y dias de alerta. |
| RF-10 Proveedores y sucursales | Implementado: alta, consulta y eliminacion. |
| RF-11 Usuarios, autenticacion y roles | Implementado con contrasenas hasheadas, JWT y permisos por rol; ver seccion 7. |
| RF-12 API HTTP/REST para frontend | Implementado para el backend. La aplicacion frontend no esta incluida en este repositorio. |
| RNF-01 Arquitectura limpia | Implementada mediante capas `domain`, `application`, `infrastructure` y `presentation`. |
| RNF-02 PostgreSQL y ORM | Implementado mediante SQLAlchemy; tambien se puede usar SQLite para pruebas locales. |
| RNF-03/04 Seguridad y configuracion | JWT, hash de contrasenas y configuracion mediante variables de entorno. Cambiar la clave secreta de desarrollo antes de publicar. |
| RNF-05 Mantenibilidad | Modulos por dominio y repositorios/casos de uso. |
| RNF-06 REST, JSON y OpenAPI | Implementado con FastAPI; Swagger esta disponible en `/docs`. |
| RNF-07 Interfaz web | No verificable ni implementada en este repositorio: no contiene los archivos React mencionados en el PDF. |
| RNF-08 Validacion e integridad | Esquemas Pydantic y claves foraneas; la cobertura de reglas de negocio varia por endpoint. |
| RNF-09 Trazabilidad de eventos | Implementada para operaciones como recepcion, inspeccion, cambio de estado y despacho. |

## 3. Cambios agregados o mejorados despues del documento anterior

### 3.1 Lotes compuestos por varios medicamentos

Ahora un lote puede compartir un codigo, proveedor, sucursal, recepcion y fecha
de vencimiento, y contener varios medicamentos. Cada medicamento conserva su
propia cantidad recibida y disponible.

- Se agrego la relacion `lote_productos` entre lote y medicamento.
- El codigo del lote se genera al recibir si no se envia.
- La respuesta del lote incluye la lista `productos`.
- Los reportes de inventario y alertas recorren los productos de cada lote.
- La inspeccion de calidad aprueba o rechaza el lote completo.

Ejemplo para `POST /lotes/`:

```json
{
  "proveedor_id": 1,
  "sucursal_id": 1,
  "fecha_recepcion": "2026-09-30",
  "fecha_vencimiento": "2027-09-30",
  "productos": [
    {"medicamento_id": 1, "cantidad_recibida": 100},
    {"medicamento_id": 2, "cantidad_recibida": 50}
  ]
}
```

Por compatibilidad, el formato previo de un lote con `medicamento_id` y
`cantidad_recibida` sigue aceptandose como un lote con un solo producto. Para
registrar lotes independientes en una llamada, se mantiene
`POST /lotes/recepciones`; cada elemento representa un lote distinto y puede
tener su propio codigo y vencimiento.

### 3.2 Despacho de varios lotes/productos a una sucursal

Se agrego `POST /despachos/multiple`. Se envia una sucursal y una lista de
productos; cada linea indica lote, medicamento y cantidad. Antes de guardar, el
backend valida que los lotes esten aprobados, que el medicamento pertenezca al
lote y que haya stock suficiente. El descuento se hace en el stock del
medicamento de esa linea. Cada linea crea un despacho individual que conserva
el codigo del lote de origen.

```json
{
  "sucursal_id": 2,
  "productos": [
    {"lote_id": 10, "medicamento_id": 1, "cantidad_despachada": 20},
    {"lote_id": 11, "medicamento_id": 2, "cantidad_despachada": 15}
  ]
}
```

El endpoint anterior `POST /despachos/` sigue disponible para un despacho
individual.

### 3.3 Alertas de vencimiento

`GET /reportes/alertas/vencimiento` incluye lotes aprobados con existencias
que ya vencieron y los que estan dentro del periodo de alerta definido por
`dias_alerta_vencimiento` para cada medicamento. Cada elemento contiene:

- `estado_alerta`: `vencido` o `por_vencer`.
- `dias_restantes`: dias hasta el vencimiento; es negativo para indicar dias
  transcurridos desde que vencio.

Las alertas se calculan cuando se consulta la API. No se envian notificaciones
automaticas ni correos.

### 3.4 Alertas de bajo stock

`GET /lotes/alertas/bajo-stock` calcula stock por medicamento y sucursal. El
umbral de consulta es general para la solicitud, con valor predeterminado 10,
y puede cambiarse, por ejemplo, con `?umbral=5`.

Solo se cuentan lotes aprobados y no vencidos. La consulta suma cantidades de
`lote_productos` y mantiene compatibilidad con lotes antiguos que todavia no
tienen productos asociados, usando en ese caso los campos historicos de `lotes`.
El script `scripts/seed.py` tambien crea la relacion del producto y sincroniza
los descuentos de los despachos de prueba.

> El umbral configurable por medicamento mencionado como posible mejora no
> esta implementado: actualmente hay un solo parametro `umbral` por consulta.

### 3.5 Reportes de inventario

`GET /reportes/inventario` permite combinar filtros opcionales:

- `proveedor_id`
- `medicamento_id`
- `fecha_desde`
- `fecha_hasta`

Las fechas filtran por fecha de vencimiento y se pueden utilizar sin seleccionar
un medicamento. Si `fecha_desde` es posterior a `fecha_hasta`, la API responde
con HTTP 400.

### 3.6 Administracion de usuarios y permisos

- El primer usuario registrado obtiene el rol `administrador`.
- Los registros posteriores reciben `personal_sucursal`.
- `GET /usuarios/` lista las cuentas.
- `PATCH /usuarios/{user_id}/rol` permite al administrador cambiar el rol.
- No se permite degradar al ultimo administrador.
- Roles definidos: `administrador`, `almacen`, `personal_calidad`,
  `personal_sucursal`, `proveedor` y `ente_regulador`.

Esta gestion se realiza en el backend. La pantalla de perfil, cambios visuales
de login/registro y la interfaz React no forman parte del codigo presente.

### 3.7 Fechas y horas sin zona horaria

Las columnas `DateTime` de los modelos se configuran sin zona horaria. La
confirmacion de recepcion usa hora local sin `tzinfo`; la expiracion JWT se
calcula como tiempo Unix para conservar el plazo de expiracion del token. Al
iniciar el backend, PostgreSQL convierte las columnas horarias existentes a
`TIMESTAMP WITHOUT TIME ZONE`.

## 4. Instalacion y ejecucion

### Usando el entorno virtual existente

Si el entorno `venv` ya esta creado, no hace falta crear otro:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Si las dependencias ya estan instaladas, ejecutar directamente:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Abrir `http://127.0.0.1:8000/docs` para Swagger.

### Configuracion de base de datos

La variable `DATABASE_URL` selecciona la base. PostgreSQL se configura con una
cadena compatible con SQLAlchemy; SQLite es el valor por defecto si no se
configura `DATABASE_URL`.

Ejemplos de formato:

```text
DATABASE_URL=postgresql+psycopg2://localhost:5432/farmacia_db
DATABASE_URL=sqlite:///./farmaceutica.db
```

La seguridad lee tambien `SECRET_KEY`, `ALGORITHM` y
`ACCESS_TOKEN_EXPIRE_MINUTES`. Un `.env` local puede tener esta estructura:

```dotenv
DATABASE_URL=postgresql+psycopg2://localhost:5432/farmacia_db
SECRET_KEY=REEMPLAZAR_POR_UN_SECRETO_LARGO_Y_ALEATORIO
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Si la instancia PostgreSQL requiere usuario y contrasena, configura la URL
completa localmente o utiliza el mecanismo de credenciales de tu entorno; no
incluyas credenciales reales en README ni en el repositorio.
Usar una `SECRET_KEY` privada y robusta fuera de desarrollo. No publicar el
archivo `.env` ni compartir sus valores. Si no se define `DATABASE_URL`, se
utiliza `sqlite:///./farmaceutica.db`.

## 5. Flujo sugerido de prueba

1. `POST /auth/registro` para crear el primer usuario administrador.
2. `POST /auth/login` para obtener un token; en Swagger usar **Authorize**.
3. Crear catalogos: `POST /medicamentos/`, `POST /proveedores/` y
   `POST /sucursales/`.
4. Recibir un lote simple o compuesto mediante `POST /lotes/`.
5. Registrar inspeccion aprobado/rechazado con `POST /inspecciones/`.
6. Consultar bajo stock con `GET /lotes/alertas/bajo-stock?umbral=10`.
7. Despachar individualmente con `POST /despachos/` o varias lineas con
   `POST /despachos/multiple`.
8. Confirmar recepcion con `PATCH /despachos/{despacho_id}/confirmar`.
9. Registrar temperatura con `POST /monitoreo-temperatura/`.
10. Consultar historial con `GET /trazabilidad/lote/{lote_id}`.
11. Consultar inventario con `GET /reportes/inventario` y alertas de vencimiento
    con `GET /reportes/alertas/vencimiento`.
12. Gestionar roles con `GET /usuarios/` y
    `PATCH /usuarios/{user_id}/rol` como administrador.

## 6. Endpoints principales

Todas las rutas de negocio, excepto registro e inicio de sesion, requieren
autenticacion y los permisos indicados.

| Modulo | Metodo y ruta | Funcion |
|---|---|---|
| Autenticacion | `POST /auth/registro` | Registrar usuario; primer usuario es administrador. |
| Autenticacion | `POST /auth/login` | Iniciar sesion y recibir JWT. |
| Usuarios | `GET /usuarios/` | Listar usuarios; permiso `usuarios.gestionar`. |
| Usuarios | `PATCH /usuarios/{user_id}/rol` | Cambiar rol; permiso `usuarios.gestionar`. |
| Medicamentos | `GET /medicamentos/`, `GET /medicamentos/{id}` | Listar y consultar; `medicamentos.consultar`. |
| Medicamentos | `POST /medicamentos/`, `PUT /medicamentos/{id}`, `DELETE /medicamentos/{id}` | Mantener ficha tecnica; `medicamentos.gestionar`. |
| Proveedores | `GET /proveedores/`, `GET /proveedores/{id}` | Consultar; `proveedores.consultar`. |
| Proveedores | `POST /proveedores/`, `DELETE /proveedores/{id}` | Mantener proveedores; `proveedores.gestionar`. |
| Sucursales | `GET /sucursales/`, `GET /sucursales/{id}` | Consultar; `sucursales.consultar`. |
| Sucursales | `POST /sucursales/`, `DELETE /sucursales/{id}` | Mantener sucursales; `sucursales.gestionar`. |
| Lotes | `GET /lotes/`, `GET /lotes/{id}` | Listar y consultar; `lotes.consultar`. |
| Lotes | `POST /lotes/`, `POST /lotes/recepciones`, `PATCH /lotes/{id}/estado` | Recepcion y cambios de estado; `lotes.gestionar`. |
| Lotes | `GET /lotes/alertas/bajo-stock?umbral=10` | Alertas por medicamento/sucursal; `lotes.consultar`. |
| Calidad | `GET /inspecciones/`, `GET /inspecciones/lote/{id}`, `POST /inspecciones/` | Historial e inspeccion; `calidad.gestionar`. |
| Despachos | `GET /despachos/`, `POST /despachos/` | Consultar/crear despacho individual; `despachos.gestionar`. |
| Despachos | `POST /despachos/multiple` | Varias lineas hacia una sucursal; `despachos.gestionar`. |
| Despachos | `PATCH /despachos/{id}/confirmar` | Confirmar recepcion; `despachos.gestionar`. |
| Temperatura | `GET /monitoreo-temperatura/`, `POST /monitoreo-temperatura/` | Consultar y registrar lecturas; `temperatura.gestionar`. |
| Trazabilidad | `GET /trazabilidad/`, `GET /trazabilidad/lote/{id}` | Historial de eventos; `trazabilidad.consultar`. |
| Reportes | `GET /reportes/` | Listar reportes guardados; `reportes.consultar`. |
| Reportes | `GET /reportes/inventario` | Filtrar inventario; `reportes.consultar`. |
| Reportes | `GET /reportes/alertas/vencimiento` | Alertas de vencimiento; `reportes.consultar`. |
| Reportes | `POST /reportes/` | Crear registro de reporte; `reportes.consultar`. |

## 7. Seguridad y roles

Las contrasenas se almacenan con hash y la API usa JWT. Los roles y sus permisos
se inicializan desde `app/infrastructure/security/authorization.py`.

| Rol | Uso previsto |
|---|---|
| `administrador` | Gestion global, consultas y gestion de usuarios. |
| `almacen` | Gestion de lotes, temperatura y consultas relacionadas. |
| `personal_calidad` | Inspecciones y consulta de lotes/trazabilidad. |
| `personal_sucursal` | Consulta de lotes/sucursales y gestion de despachos. |
| `proveedor` | Consultas y operaciones asignadas a proveedor/lotes. |
| `ente_regulador` | Consulta de trazabilidad y reportes. |

El registro publico no permite elegir rol: la aplicacion asigna el inicial segun
si existen usuarios. El administrador cambia el rol despues del registro.

## 8. Persistencia y compatibilidad de datos

Al iniciar, `app/main.py` crea las tablas declaradas por SQLAlchemy y ejecuta
`migrate_inventory_schema()`:

- Copia la relacion producto/cantidad de lotes anteriores a `lote_productos`
  cuando corresponde.
- Completa el medicamento de despachos antiguos.
- En PostgreSQL, convierte campos `DateTime` existentes a tipo sin zona.

La migracion no reemplaza un sistema formal de migraciones versionadas. Antes de
actualizar una base de produccion, realizar un respaldo y probar la migracion
con una copia de los datos.

## 9. Datos de prueba

`scripts/seed.py` carga datos de prueba de forma idempotente y evita duplicar
registros con los codigos `SEED-*`. Puede ejecutarse con el entorno del proyecto:

```powershell
.\venv\Scripts\python.exe -m scripts.seed
```

Acepta parametros para cantidades, por ejemplo:

```powershell
.\venv\Scripts\python.exe -m scripts.seed --lotes 20 --medicamentos 10 --despachos 5
```

No ejecutar sobre produccion sin revisar el destino de base y el alcance de los
datos de prueba.

## 10. Subsistemas del modelo de comportamiento

| Subsistema | Implementacion principal |
|---|---|
| 1.0 Recepcion de mercancia | `lote_router`, `registrar_recepcion.py`, modelos `lotes` y `lote_productos`. |
| 2.0 Verificacion de calidad | `inspeccion_calidad_router`, caso de uso `inspeccion_calidad`. |
| 3.0 Distribucion y despacho | `despacho_router`, casos de uso de despacho y descuento de stock. |
| 4.0 Cadena de frio | `monitoreo_temperatura_router` y modelo de lecturas. |
| 5.0 Vencimientos y bajas | Alertas de vencimiento, filtro de stock vigente y actualizacion de estado de lote. |
| 6.0 Trazabilidad y reportes | Routers de trazabilidad y reportes, consultas de inventario. |
| 7.0 Datos tecnicos de medicamentos | Router y casos de uso de medicamentos. |

## 11. Limitaciones y trabajo pendiente

- No se incluye el frontend React citado en el PDF: formularios, tablas, estilos
  de login/registro y perfil requieren el proyecto de interfaz.
- Las alertas son consultas bajo demanda, no tareas programadas ni notificaciones
  por correo/push.
- El umbral de bajo stock es general por peticion, no configurable por
  medicamento.
- Las fechas y filtros existen en `GET /reportes/inventario`, pero no se verifico
  una interfaz visual en este repositorio.
- La lectura de temperatura registra desviaciones con limites generales
  codificados en el router; debe conectarse a la ficha tecnica si se requiere
  validar por medicamento.
- No se encontro flujo automatico para baja/descarte ni generacion periodica de
  reportes regulatorios.
- Se recomienda introducir migraciones versionadas (por ejemplo, Alembic) antes
  de nuevos cambios estructurales en bases persistentes.

## 12. Verificaciones realizadas durante los cambios

Las pruebas focalizadas ejecutadas durante esta implementacion usaron SQLite en
memoria para validar los flujos sin alterar la base de datos configurada del
proyecto. Se verificaron recepcion con multiples productos, stock por
medicamento, alertas y filtros por estado/vencimiento, despacho multiple,
compatibilidad de lotes antiguos, migracion de datos y serializacion de fechas.
Tambien se ejecutaron compilacion de Python y `git diff --check`.

Estas pruebas no sustituyen una validacion de extremo a extremo del frontend ni
una ejecucion contra una copia de produccion PostgreSQL.
