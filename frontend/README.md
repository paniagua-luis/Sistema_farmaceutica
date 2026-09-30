# FarmaControl — documentación del sistema

FarmaControl es una aplicación web para registrar y consultar operaciones de inventario farmacéutico: catálogos, recepción y calidad de lotes, existencias, despacho a sucursales, monitoreo de temperatura, alertas, trazabilidad y reportes.

Este documento describe el frontend React y su integración con el backend FastAPI del proyecto `sistema-farmaceutica`. Se puede utilizar como fuente para elaborar la documentación funcional y técnica del sistema. Los contratos HTTP descritos corresponden a los routers y esquemas revisados; la autorización efectiva siempre la aplica el backend.

## 1. Propósito y alcance

El sistema apoya el seguimiento de medicamentos desde su recepción hasta su distribución:

1. Se mantienen catálogos de medicamentos, proveedores y sucursales.
2. Se reciben lotes; un lote puede incluir más de un medicamento, cada uno con su cantidad.
3. Calidad inspecciona el lote completo y lo aprueba o rechaza.
4. Solo el inventario aprobado y vigente se ofrece para despacho y se incluye en el stock bajo.
5. Un despacho puede incluir varios productos/lotes y se dirige a una sucursal.
6. Se registran lecturas de temperatura, trazabilidad, alertas y reportes.
7. El administrador puede consultar usuarios y cambiar sus roles.

El sistema no envía notificaciones externas por las alertas: estas se calculan cuando se consulta su endpoint.

## 2. Arquitectura

### Backend

El backend usa FastAPI y SQLAlchemy, con capas inspiradas en Clean Architecture:

```text
app/
  domain/          Entidades y contratos de repositorios
  application/     Casos de uso
  infrastructure/  Persistencia SQLAlchemy, repositorios y seguridad
  presentation/    Routers HTTP, dependencias y esquemas Pydantic
  main.py          Creación de la aplicación y montaje de routers
```

Al iniciar, `app.main` crea las tablas, ejecuta la migración de inventario y configura los permisos/roles.

### Frontend

El frontend utiliza React, Vite y React Router:

```text
src/
  api/client.js       Cliente HTTP y funciones API por recurso
  components/         Layout, Navbar, rutas protegidas y componentes comunes
  context/            Estado de autenticación
  pages/              Pantallas de cada módulo
  utils/              Permisos, JWT y utilidades de fecha/hora
```

El frontend controla la navegación y ayuda a evitar acciones inválidas, pero no es una frontera de seguridad. La API backend valida token, permiso, datos y reglas del negocio.

## 3. Tecnologías

| Capa | Tecnologías |
|---|---|
| Interfaz | React 19, React DOM, React Router 6 |
| Herramientas frontend | Vite, ESLint |
| PDF | jsPDF, generación local en el navegador |
| API | FastAPI, Uvicorn, Pydantic |
| Persistencia backend | SQLAlchemy; SQLite por defecto o PostgreSQL |
| Autenticación | OAuth2 password form y JWT |

## 4. Preparación del entorno

### 4.1 Backend

Desde la raíz del repositorio (donde se encuentra `requirements.txt`):

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Configura `DATABASE_URL` en un archivo `.env` en la raíz del backend. Si no se establece, el backend usa SQLite en `sqlite:///./farmaceutica.db`. Ejemplos de formato:

```dotenv
# SQLite local
DATABASE_URL=sqlite:///./farmaceutica.db

# PostgreSQL (rellena con valores de tu entorno; no guardes credenciales en Git)
# DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST:5432/BASE
```

Inicia la API:

```powershell
uvicorn app.main:app --reload
```

Documentación interactiva: `http://127.0.0.1:8000/docs`.

Dependencias Python declaradas: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `psycopg2-binary`, `python-dotenv`, `passlib[bcrypt]`, `python-jose[cryptography]` y `python-multipart`.

### 4.2 Frontend

Desde la carpeta `frontend` del repositorio:

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

La aplicación se abre normalmente en `http://localhost:5173`.

La URL del backend se configura con `VITE_API_URL` en el archivo `.env` local:

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

Comandos disponibles:

```powershell
npm run dev       # servidor de desarrollo
npm run build     # compilación de producción
npm run lint      # ESLint
npm run preview   # servir localmente la compilación
```

## 5. Inicio de sesión y usuarios

### Registro

`POST /auth/registro` recibe `username` y `password`. El primer usuario de la base de datos queda con rol `administrador`; los siguientes se registran como `personal_sucursal`. El registro no permite seleccionar libremente el rol.

### Inicio de sesión

`POST /auth/login` recibe formulario `application/x-www-form-urlencoded` con `username` y `password`. Devuelve un `access_token` y el tipo de token. Las llamadas protegidas envían:

```http
Authorization: Bearer <access_token>
```

El frontend guarda el token, el nombre de usuario y el rol en `localStorage`. El rol del JWT se usa para presentar el menú y proteger rutas en la interfaz; el backend vuelve a validar el permiso en cada endpoint.

### Perfil y administración de roles

- `/perfil` muestra el usuario y el rol de la sesión; no modifica los datos.
- `/usuarios` es una pantalla administrativa visible solo a quien tiene `usuarios.gestionar`.
- El backend lista usuarios con `GET /usuarios/`.
- El administrador cambia el rol con `PATCH /usuarios/{user_id}/rol` y JSON `{ "rol": "almacen" }`.
- Roles reconocidos: `administrador`, `almacen`, `personal_calidad`, `personal_sucursal`, `proveedor`, `ente_regulador`.
- El backend impide retirar el rol al último administrador.
- Si un administrador cambia su propio rol desde la interfaz, esta cierra su sesión para que vuelva a entrar con el rol actualizado.

## 6. Roles y permisos

Permisos definidos actualmente por el backend (`app/infrastructure/security/authorization.py`):

| Rol | Capacidades principales |
|---|---|
| `administrador` | Gestionar catálogos, lotes, calidad, despachos, temperatura y usuarios; consultar reportes y trazabilidad |
| `almacen` | Gestionar lotes y temperatura; consultar trazabilidad y reportes |
| `personal_calidad` | Gestionar calidad y temperatura; consultar lotes, trazabilidad y reportes |
| `personal_sucursal` | Gestionar despachos; consultar lotes y sucursales |
| `proveedor` | Gestionar lotes; consultar lotes, medicamentos, proveedores y sucursales |
| `ente_regulador` | Consultar trazabilidad y reportes |

Permisos relevantes:

| Permiso | Uso |
|---|---|
| `medicamentos.consultar` / `medicamentos.gestionar` | Consultar o modificar catálogo de medicamentos |
| `proveedores.consultar` / `proveedores.gestionar` | Consultar o modificar proveedores |
| `sucursales.consultar` / `sucursales.gestionar` | Consultar o modificar sucursales |
| `lotes.consultar` / `lotes.gestionar` | Consultar o gestionar lotes e inventario |
| `calidad.gestionar` | Inspecciones de calidad |
| `despachos.gestionar` | Registrar y confirmar despachos |
| `temperatura.gestionar` | Lecturas de cadena de frío |
| `trazabilidad.consultar` | Consulta de eventos de trazabilidad |
| `reportes.consultar` | Consulta de informes, inventario y alertas de vencimiento |
| `usuarios.gestionar` | Listar cuentas y cambiar roles |

La matriz visual del frontend se encuentra en `src/utils/permisos.js` y debe mantenerse sincronizada con el backend. Actualmente el frontend tiene además el permiso de interfaz `reportes.generar`, mientras que el router backend de reportes aplica `reportes.consultar` al conjunto de sus operaciones, incluido `POST /reportes/`. Revisar esta diferencia al cambiar la política de generación de reportes.

## 7. Módulos y reglas de negocio

### 7.1 Catálogos

- **Medicamentos**: código, nombre, principio activo, rango de temperatura y días de aviso de vencimiento. La pantalla presenta el vencimiento más próximo de sus lotes aprobados con existencias.
- **Proveedores**: catálogo asociado a recepciones de lotes.
- **Sucursales**: catálogo de ubicaciones a las que se asigna inventario y se envían despachos.

Los campos exactos de creación y actualización están definidos en los esquemas Pydantic de cada recurso y se publican en `/docs`.

### 7.2 Recepción e inventario

Un lote contiene código, proveedor, sucursal de inventario, fecha de recepción, fecha de vencimiento y productos. Todos los productos del lote comparten sus datos generales y vencimiento.

Ejemplo de lote compuesto en `POST /lotes/`:

```json
{
  "proveedor_id": 1,
  "sucursal_id": 1,
  "fecha_recepcion": "2026-09-30",
  "fecha_vencimiento": "2027-09-30",
  "productos": [
    { "medicamento_id": 1, "cantidad_recibida": 100 },
    { "medicamento_id": 2, "cantidad_recibida": 50 }
  ]
}
```

Reglas principales:

- Se admite la forma de un solo medicamento (`medicamento_id` y `cantidad_recibida`) o la lista `productos`; no se deben enviar ambas formas a la vez.
- `productos` requiere al menos un elemento y no permite repetir el mismo medicamento dentro del lote.
- Las cantidades deben ser enteros positivos.
- La inspección se aplica al lote completo.
- Para registrar varios lotes independientes en una operación se usa `POST /lotes/recepciones`, con `{ "lotes": [ ... ] }`.
- Cambiar estado de lote admite estados del flujo como `pendiente_verificacion`, `aprobado`, `rechazado`, `vencido` y `dado_de_baja`.

### 7.3 Calidad

Un usuario con `calidad.gestionar` registra una inspección de un lote. El resultado aprueba o rechaza el lote completo, y queda asociado a la trazabilidad.

### 7.4 Stock bajo

`GET /lotes/alertas/bajo-stock` consulta existencias agregadas por medicamento y sucursal. El parámetro `umbral` es opcional, debe ser mayor que cero y por defecto vale 10.

El cálculo backend revisado suma existencias de lotes aprobados cuya fecha de vencimiento no ha pasado. Existencias de lotes pendientes, rechazados, dados de baja o vencidos no se cuentan para este indicador. La respuesta informa medicamento, sucursal, stock disponible y umbral.

### 7.5 Distribución y despacho

Los despachos se hacen desde lotes aprobados y se descuentan del stock del medicamento correspondiente. La interfaz permite preparar varias líneas para una misma sucursal.

`POST /despachos/multiple` usa este formato:

```json
{
  "sucursal_id": 2,
  "productos": [
    { "lote_id": 10, "medicamento_id": 1, "cantidad_despachada": 20 },
    { "lote_id": 11, "medicamento_id": 2, "cantidad_despachada": 15 }
  ]
}
```

Cada pareja `lote_id` / `medicamento_id` debe ser única en la solicitud. La interfaz suma automáticamente las cantidades si el usuario repite una pareja en distintas líneas. El backend valida lotes y stock antes de guardar el conjunto. Cada producto crea un despacho independiente con su código y estado.

El endpoint individual `POST /despachos/` se conserva. La recepción física se confirma con `PATCH /despachos/{id}/confirmar`.

### 7.6 Temperatura

El módulo registra lecturas de cadena de frío asociadas a una ubicación y opcionalmente a un lote. La lectura se marca de acuerdo con las reglas del caso de uso y genera eventos de trazabilidad cuando corresponda. La fecha/hora se almacena como timestamp; el frontend oculta el sufijo de zona horaria al presentarlo.

### 7.7 Trazabilidad

La trazabilidad guarda eventos de operaciones como recepción, inspección, despacho y movimientos de stock. Se consulta toda la secuencia o el historial de un lote. Los endpoints de consulta requieren `trazabilidad.consultar`.

### 7.8 Reportes y PDF

La pantalla `/reportes` permite consultar inventario por proveedor, medicamento o rango de fechas de vencimiento. Para el rango, el medicamento es opcional.

- `GET /reportes/` lista reportes guardados.
- `GET /reportes/inventario` admite `proveedor_id`, `medicamento_id`, `fecha_desde` y `fecha_hasta`.
- `GET /reportes/alertas/vencimiento` consulta lotes dentro del plazo de alerta y vencidos, de acuerdo con la respuesta del backend.
- `POST /reportes/` guarda un reporte.
- Los botones **Descargar PDF** generan el PDF en el navegador mediante jsPDF a partir del reporte ya listado. No es una descarga binaria del backend.
- Consultar y descargar un reporte existente no requiere permiso para generar/guardar. El rol `ente_regulador` cuenta con `reportes.consultar`.

## 8. Catálogo de API

Las rutas siguientes están montadas por el backend FastAPI. El detalle de modelos, campos obligatorios, ejemplos y códigos de respuesta está disponible en Swagger (`/docs`).

| Método | Ruta | Operación | Permiso |
|---|---|---|---|
| `POST` | `/auth/registro` | Crear cuenta y asignar rol inicial automáticamente | Público |
| `POST` | `/auth/login` | Iniciar sesión y obtener token | Público |
| `GET` | `/usuarios/` | Listar usuarios | `usuarios.gestionar` |
| `PATCH` | `/usuarios/{user_id}/rol` | Cambiar rol | `usuarios.gestionar` |
| `GET` | `/medicamentos/` | Listar medicamentos | `medicamentos.consultar` |
| `GET` | `/medicamentos/{medicamento_id}` | Obtener medicamento | `medicamentos.consultar` |
| `POST` | `/medicamentos/` | Crear medicamento | `medicamentos.gestionar` |
| `PUT` | `/medicamentos/{medicamento_id}` | Actualizar medicamento | `medicamentos.gestionar` |
| `DELETE` | `/medicamentos/{medicamento_id}` | Eliminar medicamento | `medicamentos.gestionar` |
| `GET` | `/proveedores/` | Listar proveedores | `proveedores.consultar` |
| `GET` | `/proveedores/{proveedor_id}` | Obtener proveedor | `proveedores.consultar` |
| `POST` | `/proveedores/` | Crear proveedor | `proveedores.gestionar` |
| `DELETE` | `/proveedores/{proveedor_id}` | Eliminar proveedor | `proveedores.gestionar` |
| `GET` | `/sucursales/` | Listar sucursales | `sucursales.consultar` |
| `GET` | `/sucursales/{sucursal_id}` | Obtener sucursal | `sucursales.consultar` |
| `POST` | `/sucursales/` | Crear sucursal | `sucursales.gestionar` |
| `DELETE` | `/sucursales/{sucursal_id}` | Eliminar sucursal | `sucursales.gestionar` |
| `GET` | `/lotes/` | Listar lotes | `lotes.consultar` |
| `GET` | `/lotes/{lote_id}` | Obtener lote | `lotes.consultar` |
| `GET` | `/lotes/alertas/bajo-stock` | Alertas de stock bajo | `lotes.consultar` |
| `POST` | `/lotes/` | Recibir un lote | `lotes.gestionar` |
| `POST` | `/lotes/recepciones` | Recibir varios lotes independientes | `lotes.gestionar` |
| `PATCH` | `/lotes/{lote_id}/estado` | Cambiar estado de lote | `lotes.gestionar` |
| `GET` | `/inspecciones/` | Listar inspecciones | `calidad.gestionar` |
| `GET` | `/inspecciones/lote/{lote_id}` | Historial de inspección de lote | `calidad.gestionar` |
| `POST` | `/inspecciones/` | Registrar inspección | `calidad.gestionar` |
| `GET` | `/despachos/` | Listar despachos | `despachos.gestionar` |
| `POST` | `/despachos/` | Registrar un despacho | `despachos.gestionar` |
| `POST` | `/despachos/multiple` | Despachar múltiples productos/lotes a una sucursal | `despachos.gestionar` |
| `PATCH` | `/despachos/{despacho_id}/confirmar` | Confirmar recepción en sucursal | `despachos.gestionar` |
| `GET` | `/monitoreo-temperatura/` | Listar lecturas | `temperatura.gestionar` |
| `POST` | `/monitoreo-temperatura/` | Registrar lectura | `temperatura.gestionar` |
| `GET` | `/trazabilidad/` | Listar eventos | `trazabilidad.consultar` |
| `GET` | `/trazabilidad/lote/{lote_id}` | Historial de eventos por lote | `trazabilidad.consultar` |
| `GET` | `/reportes/` | Listar reportes | `reportes.consultar` |
| `GET` | `/reportes/inventario` | Consultar inventario con filtros | `reportes.consultar` |
| `GET` | `/reportes/alertas/vencimiento` | Consultar alertas de vencimiento | `reportes.consultar` |
| `POST` | `/reportes/` | Guardar reporte | El router aplica `reportes.consultar` |

## 9. Flujo funcional recomendado

1. Levantar el backend y el frontend.
2. Registrar la primera cuenta; se convierte en administrador.
3. Iniciar sesión y crear medicamentos, proveedores y sucursales.
4. Desde **Usuarios**, el administrador cambia los roles de otras cuentas según sus responsabilidades.
5. Registrar uno o varios lotes y sus productos.
6. Realizar inspección de calidad; aprobar el lote para que sus existencias puedan despacharse.
7. Preparar una distribución: elegir una sucursal y agregar lotes/productos/cantidades.
8. Confirmar la recepción de cada despacho desde el historial.
9. Registrar lecturas de temperatura.
10. Consultar alertas, reportes y trazabilidad.

El flujo de eventos de referencia es recepción (1), calidad (2/13), despacho (3/4/14), recepción confirmada (5), trazabilidad (6/7), reportes (8/9/20) y temperatura (16/19). La numeración es una referencia del dominio del proyecto.

## 10. Navegación del frontend

| Ruta | Pantalla |
|---|---|
| `/login` | Inicio de sesión |
| `/registro` | Registro |
| `/` | Panel principal |
| `/medicamentos` | Catálogo de medicamentos |
| `/proveedores` | Catálogo de proveedores |
| `/sucursales` | Catálogo de sucursales |
| `/lotes` | Recepción y listado de lotes |
| `/alertas` | Alertas de stock bajo |
| `/inspecciones` | Control de calidad |
| `/despachos` | Distribución y despacho múltiple |
| `/monitoreo` | Cadena de frío |
| `/trazabilidad` | Eventos e historial por lote |
| `/reportes` | Consultas, alertas de vencimiento e historial/PDF |
| `/perfil` | Usuario y rol de la sesión |
| `/usuarios` | Gestión de roles reservada al administrador |

Las rutas de módulos se protegen por permiso en el frontend. El backend vuelve a validar cada endpoint.

## 11. Modelo conceptual de información

Entidades principales:

- **Usuario**: credenciales de acceso y rol.
- **Medicamento**: datos técnicos, temperatura y plazo de alerta de vencimiento.
- **Proveedor** y **Sucursal**: catálogos referenciados por los lotes.
- **Lote**: código, proveedor, sucursal de almacenamiento, recepción, vencimiento y estado.
- **LoteProducto**: relación entre lote y medicamento, con cantidad recibida y disponible por producto.
- **Inspección de calidad**: resultado de revisar un lote.
- **Despacho**: lote, medicamento, sucursal destino, cantidad y estado de recepción.
- **Lectura de temperatura**: valor, ubicación, fecha/hora y posible referencia al lote.
- **Reporte**: informe guardado, destinatario, tipo, contenido y lote opcional.
- **Trazabilidad**: eventos, descripción, usuario y posible referencia al lote.

Un lote compuesto contiene una o más filas `LoteProducto`; la existencia de cada medicamento se mantiene individualmente en esa relación.

## 12. Errores y diagnóstico

- **401 / no autenticado**: iniciar sesión de nuevo; confirmar que el token se envía como Bearer.
- **403 / permiso insuficiente**: comprobar rol y permiso del endpoint en backend; el menú del frontend no concede autorización.
- **400 / validación o regla de negocio**: revisar cantidades positivas, lote aprobado, stock, fechas, producto del lote y reglas de duplicados.
- **404 / recurso inexistente**: revisar el ID utilizado y que pertenezca al lote/sucursal esperado.
- **Error de carga de PDF en desarrollo**: reiniciar Vite forzando la optimización (`npm run dev -- --force`) y recargar el navegador; el botón de la página de reportes permite reintentar la carga de jsPDF.
- **Stock reportado como cero**: revisar si las unidades están en lotes aprobados, vigentes y en la sucursal mostrada; el cálculo de stock bajo excluye lotes no elegibles.
- Los mensajes concretos de error de API suelen aparecer en pantalla; consultar también la respuesta JSON y los logs del backend.

## 13. Validación y pruebas

En el frontend:

```powershell
npm run lint
npm run build
```

La interfaz valida campos antes de enviar, pero las reglas críticas deben permanecer en el backend. Para probar un flujo completo, utilizar datos no productivos y comprobar cada operación en Swagger, en la base de datos y en la interfaz.

## 14. Seguridad y operación

- No almacenar contraseñas, tokens reales ni cadenas de conexión en este README ni en Git.
- Mantener `.env` fuera del control de versiones; compartir solo ejemplos con valores ficticios.
- Servir en producción bajo HTTPS y configurar la URL del backend por entorno.
- Las comprobaciones de permisos del frontend mejoran la navegación, pero no sustituyen los `Depends(requiere_permiso(...))` del backend.
- Los roles y permisos deben tener una fuente de verdad coherente. Antes de añadir un rol/permisos, actualizar backend, inicialización de roles, JWT si corresponde, `src/utils/permisos.js`, las rutas y este documento.
- Verificar la política de creación de reportes: actualmente el backend protege el router completo de reportes con `reportes.consultar`, mientras el frontend usa además una distinción visual `reportes.generar`.

## 15. Mantenimiento de esta documentación

Actualizar este README cuando cambie cualquiera de estos elementos:

1. Rutas, métodos HTTP, schemas o permisos de API.
2. Roles disponibles y su asignación al registrarse.
3. Reglas de inventario, vencimiento, inspección o despacho.
4. Rutas/pantallas del frontend y responsabilidades por rol.
5. Variables de entorno, comandos de instalación o dependencias.
6. Reglas de generación/descarga de reportes o conservación de timestamps.

Para una documentación formal derivada de este README, se recomienda separar el contenido en: manual de usuario por rol, guía de instalación/operación, referencia OpenAPI, modelo de datos (DER), arquitectura y catálogo de reglas de negocio.
