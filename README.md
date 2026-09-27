# Sistema de Control de una Farmaceutica

Backend en FastAPI organizado con **Clean Architecture** (domain / application / infrastructure / presentation),
basado en el modelo ambiental, DFD y DER de la Actividad 4 (Sistemas de Informacion III).

## Estructura

```
app/
  domain/            entidades puras + interfaces de repositorio
  application/        casos de uso (services)
  infrastructure/      modelos SQLAlchemy, repositorios concretos, seguridad JWT
  presentation/         routers FastAPI, schemas Pydantic, dependencias
  main.py
```

## Instalacion

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` con tu cadena de conexion (PostgreSQL) o deja el valor por defecto (SQLite, para probar rapido sin instalar nada).

## Ejecutar

```powershell
uvicorn app.main:app --reload
```

Abre `http://127.0.0.1:8000/docs`.

## Flujo sugerido de prueba (Swagger)

1. `POST /auth/registro` -> crea un usuario (ej. rol "administrador")
2. `POST /auth/login` -> obten el token (usar "Authorize" en Swagger)
3. `POST /medicamentos/`, `POST /proveedores/`, `POST /sucursales/` -> catalogos base
4. `POST /lotes/` -> evento 1: recepcion de un lote (referencia a medicamento/proveedor/sucursal creados)
5. `POST /inspecciones/` -> eventos 2/13: aprueba o rechaza el lote
6. `POST /despachos/` -> eventos 3/4/14: despacha el lote aprobado a una sucursal
7. `PATCH /despachos/{id}/confirmar` -> evento 5: sucursal confirma recepcion
8. `GET /trazabilidad/lote/{lote_id}` -> eventos 6/7: historial completo del lote
9. `POST /monitoreo-temperatura/` -> eventos 16/19: registra lectura de temperatura
10. `POST /reportes/` -> eventos 8/9/20: genera un reporte/informe

## Mapeo eventos -> subsistema -> modulo de codigo

| Subsistema (documento) | Router | Service |
|---|---|---|
| 1.0 Recepcion de Mercancia | lote_router | LoteService |
| 2.0 Verificacion de Calidad | inspeccion_calidad_router | InspeccionCalidadService |
| 3.0 Distribucion y Despacho | despacho_router | DespachoService |
| 4.0 Monitoreo Cadena de Frio | monitoreo_temperatura_router | MonitoreoTemperaturaService |
| 5.0 Vencimientos y Bajas | lote_router (estado) | LoteService.actualizar_estado |
| 6.0 Trazabilidad y Reportes | trazabilidad_router / reporte_router | TrazabilidadService / ReporteService |
| 7.0 Datos Tecnicos de Medicamentos | medicamento_router | MedicamentoService |
