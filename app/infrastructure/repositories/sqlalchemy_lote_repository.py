from datetime import date, timedelta
from sqlalchemy import and_, func, true, union_all
from sqlalchemy.orm import Session
from app.domain.entities.lote import Lote, LoteProducto
from app.domain.repositories.lote_repository import ILoteRepository
from app.infrastructure.models.lote_model import LoteModel
from app.infrastructure.models.lote_producto_model import LoteProductoModel
from app.infrastructure.models.medicamento_model import MedicamentoModel
from app.infrastructure.models.proveedor_model import ProveedorModel
from app.infrastructure.models.sucursal_model import SucursalModel


class SQLAlchemyLoteRepository(ILoteRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, l: LoteModel) -> Lote:
        return Lote(
            id=l.id, codigo_lote=l.codigo_lote, medicamento_id=l.medicamento_id,
            proveedor_id=l.proveedor_id, sucursal_id=l.sucursal_id,
            cantidad_recibida=l.cantidad_recibida, cantidad_disponible=l.cantidad_disponible,
            fecha_recepcion=l.fecha_recepcion, fecha_vencimiento=l.fecha_vencimiento,
            estado_lote=l.estado_lote,
            productos=[
                LoteProducto(
                    medicamento_id=producto.medicamento_id,
                    cantidad_recibida=producto.cantidad_recibida,
                    cantidad_disponible=producto.cantidad_disponible,
                    medicamento=producto.medicamento.nombre,
                )
                for producto in l.productos
            ],
        )

    def get_all(self):
        return [self._a_entidad(l) for l in self.db.query(LoteModel).all()]

    def get_by_id(self, lote_id: int):
        l = self.db.query(LoteModel).filter(LoteModel.id == lote_id).first()
        return self._a_entidad(l) if l else None

    def get_by_codigo(self, codigo_lote: str):
        l = self.db.query(LoteModel).filter(LoteModel.codigo_lote == codigo_lote).first()
        return self._a_entidad(l) if l else None

    def create(self, lote: Lote):
        l = LoteModel(
            codigo_lote=lote.codigo_lote, medicamento_id=lote.medicamento_id,
            proveedor_id=lote.proveedor_id, sucursal_id=lote.sucursal_id,
            cantidad_recibida=lote.cantidad_recibida, cantidad_disponible=lote.cantidad_disponible,
            fecha_recepcion=lote.fecha_recepcion, fecha_vencimiento=lote.fecha_vencimiento,
            estado_lote=lote.estado_lote,
            productos=[
                LoteProductoModel(
                    medicamento_id=producto.medicamento_id,
                    cantidad_recibida=producto.cantidad_recibida,
                    cantidad_disponible=producto.cantidad_disponible,
                )
                for producto in lote.productos or []
            ],
        )
        self.db.add(l)
        self.db.commit()
        self.db.refresh(l)
        return self._a_entidad(l)

    def create_many(self, lotes: list[Lote]):
        modelos = [
            LoteModel(
                codigo_lote=lote.codigo_lote, medicamento_id=lote.medicamento_id,
                proveedor_id=lote.proveedor_id, sucursal_id=lote.sucursal_id,
                cantidad_recibida=lote.cantidad_recibida, cantidad_disponible=lote.cantidad_disponible,
                fecha_recepcion=lote.fecha_recepcion, fecha_vencimiento=lote.fecha_vencimiento,
                estado_lote=lote.estado_lote,
                productos=[
                    LoteProductoModel(
                        medicamento_id=producto.medicamento_id,
                        cantidad_recibida=producto.cantidad_recibida,
                        cantidad_disponible=producto.cantidad_disponible,
                    )
                    for producto in lote.productos or []
                ],
            )
            for lote in lotes
        ]
        self.db.add_all(modelos)
        self.db.flush()
        return [self._a_entidad(modelo) for modelo in modelos]

    def update(self, lote: Lote):
        l = self.db.query(LoteModel).filter(LoteModel.id == lote.id).first()
        l.estado_lote = lote.estado_lote
        l.cantidad_disponible = lote.cantidad_disponible
        cantidades_por_medicamento = {
            producto.medicamento_id: producto.cantidad_disponible
            for producto in lote.productos or []
        }
        for producto in l.productos:
            if producto.medicamento_id in cantidades_por_medicamento:
                producto.cantidad_disponible = cantidades_por_medicamento[producto.medicamento_id]
        self.db.commit()
        self.db.refresh(l)
        return self._a_entidad(l)

    def update_many_pending(self, lotes: list[Lote]) -> None:
        lotes_por_id = {lote.id: lote for lote in lotes}
        modelos = (
            self.db.query(LoteModel)
            .filter(LoteModel.id.in_(lotes_por_id))
            .all()
        )
        if len(modelos) != len(lotes_por_id):
            raise ValueError("No se encontraron todos los lotes para actualizar")

        for modelo in modelos:
            lote = lotes_por_id[modelo.id]
            modelo.cantidad_disponible = lote.cantidad_disponible
            cantidades = {
                producto.medicamento_id: producto.cantidad_disponible
                for producto in lote.productos or []
            }
            for producto in modelo.productos:
                if producto.medicamento_id in cantidades:
                    producto.cantidad_disponible = cantidades[producto.medicamento_id]
        self.db.flush()

    def get_stock_bajo(self, umbral: int):
        productos_en_lotes = self.db.query(
            LoteProductoModel.medicamento_id.label("medicamento_id"),
            LoteModel.sucursal_id.label("sucursal_id"),
            LoteProductoModel.cantidad_disponible.label("cantidad_disponible"),
            LoteModel.estado_lote.label("estado_lote"),
            LoteModel.fecha_vencimiento.label("fecha_vencimiento"),
        ).join(
            LoteModel, LoteModel.id == LoteProductoModel.lote_id,
        )
        lotes_heredados = self.db.query(
            LoteModel.medicamento_id.label("medicamento_id"),
            LoteModel.sucursal_id.label("sucursal_id"),
            LoteModel.cantidad_disponible.label("cantidad_disponible"),
            LoteModel.estado_lote.label("estado_lote"),
            LoteModel.fecha_vencimiento.label("fecha_vencimiento"),
        ).filter(
            ~self.db.query(LoteProductoModel.id).filter(
                LoteProductoModel.lote_id == LoteModel.id,
            ).exists(),
        )
        existencias = union_all(productos_en_lotes, lotes_heredados).subquery()
        stock_por_medicamento_sucursal = (
            self.db.query(
                existencias.c.medicamento_id,
                existencias.c.sucursal_id,
                func.sum(existencias.c.cantidad_disponible).label("stock_disponible"),
            )
            .filter(
                existencias.c.estado_lote == "aprobado",
                existencias.c.fecha_vencimiento >= date.today(),
            )
            .group_by(existencias.c.medicamento_id, existencias.c.sucursal_id)
            .subquery()
        )
        stock_disponible = func.coalesce(stock_por_medicamento_sucursal.c.stock_disponible, 0)
        filas = (
            self.db.query(
                MedicamentoModel.id.label("medicamento_id"),
                MedicamentoModel.nombre.label("medicamento"),
                SucursalModel.id.label("sucursal_id"),
                SucursalModel.nombre.label("sucursal"),
                stock_disponible.label("stock_disponible"),
            )
            .select_from(MedicamentoModel)
            .join(SucursalModel, true())
            .outerjoin(
                stock_por_medicamento_sucursal,
                and_(
                    stock_por_medicamento_sucursal.c.medicamento_id == MedicamentoModel.id,
                    stock_por_medicamento_sucursal.c.sucursal_id == SucursalModel.id,
                ),
            )
            .filter(stock_disponible < umbral)
            .order_by(MedicamentoModel.nombre, SucursalModel.nombre)
            .all()
        )
        return [dict(fila._mapping) | {"umbral": umbral} for fila in filas]

    def _consulta_inventario(self):
        return self.db.query(
            LoteModel.id.label("lote_id"),
            LoteModel.codigo_lote,
            LoteProductoModel.medicamento_id,
            MedicamentoModel.nombre.label("medicamento"),
            LoteModel.proveedor_id,
            ProveedorModel.nombre.label("proveedor"),
            LoteModel.sucursal_id,
            SucursalModel.nombre.label("sucursal"),
            LoteProductoModel.cantidad_recibida,
            LoteProductoModel.cantidad_disponible,
            LoteModel.fecha_vencimiento,
            LoteModel.estado_lote,
            MedicamentoModel.dias_alerta_vencimiento,
        ).join(
            LoteProductoModel, LoteProductoModel.lote_id == LoteModel.id,
        ).join(
            MedicamentoModel, MedicamentoModel.id == LoteProductoModel.medicamento_id,
        ).join(
            ProveedorModel, ProveedorModel.id == LoteModel.proveedor_id,
        ).join(
            SucursalModel, SucursalModel.id == LoteModel.sucursal_id,
        )

    def consultar_inventario(
        self,
        proveedor_id: int | None = None,
        medicamento_id: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):
        consulta = self._consulta_inventario()
        if proveedor_id is not None:
            consulta = consulta.filter(LoteModel.proveedor_id == proveedor_id)
        if medicamento_id is not None:
            consulta = consulta.filter(LoteProductoModel.medicamento_id == medicamento_id)
        if fecha_desde is not None:
            consulta = consulta.filter(LoteModel.fecha_vencimiento >= fecha_desde)
        if fecha_hasta is not None:
            consulta = consulta.filter(LoteModel.fecha_vencimiento <= fecha_hasta)
        filas = consulta.order_by(LoteModel.fecha_vencimiento, LoteModel.id, LoteProductoModel.medicamento_id).all()
        return [dict(fila._mapping) for fila in filas]

    def listar_alertas_vencimiento(self):
        hoy = date.today()
        filas = self._consulta_inventario().filter(
            LoteModel.estado_lote == "aprobado",
            LoteProductoModel.cantidad_disponible > 0,
        ).order_by(
            LoteModel.fecha_vencimiento, LoteModel.id, LoteProductoModel.medicamento_id,
        ).all()
        alertas = []
        for fila in filas:
            datos = dict(fila._mapping)
            dias_restantes = (fila.fecha_vencimiento - hoy).days
            if dias_restantes <= fila.dias_alerta_vencimiento:
                datos["dias_restantes"] = dias_restantes
                datos["estado_alerta"] = "vencido" if dias_restantes < 0 else "por_vencer"
                alertas.append(datos)
        return alertas
