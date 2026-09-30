import argparse

from sqlalchemy.orm import Session

from app.infrastructure.database import SessionLocal
from app.infrastructure.models.medicamento_model import MedicamentoModel
from app.infrastructure.models.proveedor_model import ProveedorModel
from app.infrastructure.models.sucursal_model import SucursalModel
from app.infrastructure.models.lote_model import LoteModel
from app.infrastructure.models.inspeccion_calidad_model import InspeccionCalidadModel
from app.infrastructure.models.trazabilidad_model import TrazabilidadModel
from app.infrastructure.models.despacho_model import DespachoModel
from app.infrastructure.models.monitoreo_temperatura_model import MonitoreoTemperaturaModel
from app.infrastructure.models.reporte_model import ReporteModel
from app.infrastructure.models.usuario_model import UsuarioModel
from app.infrastructure.models.lote_producto_model import LoteProductoModel
from scripts.factories import (
    despacho_data,
    inspeccion_data,
    lote_data,
    medicamento_data,
    proveedor_data,
    reporte_data,
    sucursal_data,
    temperatura_data,
    trazabilidad_data,
)


def get_or_create(session: Session, model, code_field: str, data: dict):
    code = data[code_field]
    entity = session.query(model).filter(getattr(model, code_field) == code).first()
    if entity:
        return entity, False

    entity = model(**data)
    session.add(entity)
    session.flush()
    return entity, True


def seed(
    session: Session,
    proveedores_count: int,
    sucursales_count: int,
    medicamentos_count: int,
    lotes_count: int,
    inspecciones_count: int,
    despachos_count: int,
    lecturas_count: int,
    reportes_count: int,
) -> dict[str, int]:
    created = {
        "proveedores": 0,
        "sucursales": 0,
        "medicamentos": 0,
        "lotes": 0,
        "inspecciones": 0,
        "trazabilidad": 0,
        "despachos": 0,
        "lecturas": 0,
        "reportes": 0,
    }

    proveedores = []
    for index in range(1, proveedores_count + 1):
        proveedor, was_created = get_or_create(
            session, ProveedorModel, "codigo_proveedor", proveedor_data(index)
        )
        proveedores.append(proveedor)
        created["proveedores"] += int(was_created)

    sucursales = []
    for index in range(1, sucursales_count + 1):
        sucursal, was_created = get_or_create(
            session, SucursalModel, "codigo_sucursal", sucursal_data(index)
        )
        sucursales.append(sucursal)
        created["sucursales"] += int(was_created)

    medicamentos = []
    for index in range(1, medicamentos_count + 1):
        medicamento, was_created = get_or_create(
            session, MedicamentoModel, "codigo_medicamento", medicamento_data(index)
        )
        medicamentos.append(medicamento)
        created["medicamentos"] += int(was_created)

    for index in range(1, lotes_count + 1):
        medicamento = medicamentos[(index - 1) % len(medicamentos)]
        proveedor = proveedores[(index - 1) % len(proveedores)]
        sucursal = sucursales[(index - 1) % len(sucursales)]
        _, was_created = get_or_create(
            session,
            LoteModel,
            "codigo_lote",
            lote_data(index, medicamento.id, proveedor.id, sucursal.id),
        )
        created["lotes"] += int(was_created)

    seed_lotes = session.query(LoteModel).filter(LoteModel.codigo_lote.like("SEED-LOTE-%")).order_by(LoteModel.id).all()
    for lote in seed_lotes:
        if not lote.productos:
            lote.productos.append(
                LoteProductoModel(
                    medicamento_id=lote.medicamento_id,
                    cantidad_recibida=lote.cantidad_recibida,
                    cantidad_disponible=lote.cantidad_disponible,
                )
            )
    usuarios = session.query(UsuarioModel).order_by(UsuarioModel.id).all()
    if (inspecciones_count or despachos_count or lecturas_count or reportes_count) and not usuarios:
        raise RuntimeError("Se necesita al menos un usuario para generar datos relacionados")
    usuario_id = usuarios[0].id if usuarios else None

    for index, lote in enumerate(seed_lotes[:inspecciones_count], start=1):
        lote.estado_lote = "aprobado"
        exists = session.query(InspeccionCalidadModel).filter(
            InspeccionCalidadModel.lote_id == lote.id,
        ).first()
        if not exists:
            session.add(InspeccionCalidadModel(**inspeccion_data(index, lote.id, usuario_id)))
            created["inspecciones"] += 1

    for index, lote in enumerate(seed_lotes[:lotes_count], start=1):
        trace_exists = session.query(TrazabilidadModel).filter(
            TrazabilidadModel.lote_id == lote.id,
            TrazabilidadModel.tipo_evento == "seed_prueba",
        ).first()
        if not trace_exists:
            session.add(TrazabilidadModel(**trazabilidad_data(index, lote.id, usuario_id)))
            created["trazabilidad"] += 1

    for index, lote in enumerate(seed_lotes[:despachos_count], start=1):
        despacho, was_created = get_or_create(
            session,
            DespachoModel,
            "codigo_despacho",
            despacho_data(index, lote.id, lote.sucursal_id),
        )
        if was_created:
            lote.cantidad_disponible -= despacho.cantidad_despachada
            producto = next(
                producto
                for producto in lote.productos
                if producto.medicamento_id == lote.medicamento_id
            )
            producto.cantidad_disponible -= despacho.cantidad_despachada
        created["despachos"] += int(was_created)

    for index, lote in enumerate(seed_lotes[:lecturas_count], start=1):
        _, was_created = get_or_create(
            session,
            MonitoreoTemperaturaModel,
            "codigo_lectura",
            temperatura_data(index, lote.id),
        )
        created["lecturas"] += int(was_created)

    for index, lote in enumerate(seed_lotes[:reportes_count], start=1):
        _, was_created = get_or_create(
            session,
            ReporteModel,
            "codigo_reporte",
            reporte_data(index, lote.id),
        )
        created["reportes"] += int(was_created)

    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga datos de prueba de forma idempotente.")
    parser.add_argument("--proveedores", type=int, default=5)
    parser.add_argument("--sucursales", type=int, default=3)
    parser.add_argument("--medicamentos", type=int, default=20)
    parser.add_argument("--lotes", type=int, default=50)
    parser.add_argument("--inspecciones", type=int, default=20)
    parser.add_argument("--despachos", type=int, default=10)
    parser.add_argument("--lecturas", type=int, default=20)
    parser.add_argument("--reportes", type=int, default=5)
    args = parser.parse_args()

    if min(
        args.proveedores,
        args.sucursales,
        args.medicamentos,
        args.lotes,
        args.inspecciones,
        args.despachos,
        args.lecturas,
        args.reportes,
    ) < 0:
        parser.error("Las cantidades no pueden ser negativas")
    if args.lotes and not args.medicamentos:
        parser.error("Se necesita al menos un medicamento para crear lotes")
    if args.lotes and not args.proveedores:
        parser.error("Se necesita al menos un proveedor para crear lotes")
    if args.lotes and not args.sucursales:
        parser.error("Se necesita al menos una sucursal para crear lotes")
    if max(args.inspecciones, args.despachos, args.lecturas, args.reportes) > args.lotes:
        parser.error("La cantidad de datos relacionados no puede superar la cantidad de lotes")

    session = SessionLocal()
    try:
        created = seed(
            session,
            args.proveedores,
            args.sucursales,
            args.medicamentos,
            args.lotes,
            args.inspecciones,
            args.despachos,
            args.lecturas,
            args.reportes,
        )
        session.commit()
        print("Datos creados:")
        for name, count in created.items():
            print(f"  {name}: {count}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
