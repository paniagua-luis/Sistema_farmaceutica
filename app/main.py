from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.infrastructure.database import Base, engine, migrate_inventory_schema
from app.infrastructure.models import (
    medicamento_model, proveedor_model, sucursal_model, usuario_model,
    lote_model, inspeccion_calidad_model, trazabilidad_model,
    lote_producto_model, despacho_model, reporte_model, monitoreo_temperatura_model,
    role_model,
)
from app.infrastructure.security.authorization import initialize_authorization
from app.presentation.middlewares import configurar_middlewares
from app.presentation.routers import (
    auth_router, medicamento_router, proveedor_router, sucursal_router,
    lote_router, inspeccion_calidad_router, despacho_router,
    monitoreo_temperatura_router, reporte_router, trazabilidad_router, usuario_router,
)

Base.metadata.create_all(bind=engine)
migrate_inventory_schema()
initialize_authorization()

app = FastAPI(title="Sistema de Control de una Farmaceutica")
configurar_middlewares(app)

app.include_router(auth_router.router)
app.include_router(medicamento_router.router)
app.include_router(proveedor_router.router)
app.include_router(sucursal_router.router)
app.include_router(lote_router.router)
app.include_router(inspeccion_calidad_router.router)
app.include_router(despacho_router.router)
app.include_router(monitoreo_temperatura_router.router)
app.include_router(reporte_router.router)
app.include_router(trazabilidad_router.router)
app.include_router(usuario_router.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
