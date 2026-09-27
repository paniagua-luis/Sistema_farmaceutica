from datetime import date, timedelta


def proveedor_data(index: int) -> dict:
    return {
        "nombre": f"Proveedor de prueba {index:04d}",
        "contacto": f"contacto{index:04d}@example.com",
        "codigo_proveedor": f"SEED-PROV-{index:04d}",
    }


def sucursal_data(index: int) -> dict:
    return {
        "codigo_sucursal": f"SEED-SUC-{index:04d}",
        "nombre": f"Sucursal de prueba {index:04d}",
    }


def medicamento_data(index: int) -> dict:
    return {
        "codigo_medicamento": f"SEED-MED-{index:04d}",
        "nombre": f"Medicamento de prueba {index:04d}",
        "principio_activo": f"Principio activo de prueba {index:04d}",
        "temperatura_minima": 15.0,
        "temperatura_maxima": 25.0,
        "dias_alerta_vencimiento": 30,
    }


def lote_data(index: int, medicamento_id: int, proveedor_id: int, sucursal_id: int) -> dict:
    fecha_recepcion = date.today()
    return {
        "codigo_lote": f"SEED-LOTE-{index:04d}",
        "medicamento_id": medicamento_id,
        "proveedor_id": proveedor_id,
        "sucursal_id": sucursal_id,
        "cantidad_recibida": 1000,
        "cantidad_disponible": 1000,
        "fecha_recepcion": fecha_recepcion,
        "fecha_vencimiento": fecha_recepcion + timedelta(days=730),
        "estado_lote": "pendiente_verificacion",
    }


def inspeccion_data(index: int, lote_id: int, usuario_id: int) -> dict:
    return {
        "lote_id": lote_id,
        "usuario_id": usuario_id,
        "resultado": "aprobado",
        "observaciones": f"Inspeccion de prueba {index:04d}",
    }


def trazabilidad_data(index: int, lote_id: int, usuario_id: int) -> dict:
    return {
        "lote_id": lote_id,
        "usuario_id": usuario_id,
        "tipo_evento": "seed_prueba",
        "descripcion": f"Evento de trazabilidad de prueba {index:04d}",
    }


def despacho_data(index: int, lote_id: int, sucursal_id: int) -> dict:
    return {
        "codigo_despacho": f"SEED-DESP-{index:04d}",
        "lote_id": lote_id,
        "sucursal_id": sucursal_id,
        "cantidad_despachada": 10,
        "estado_despacho": "en_transito",
    }


def temperatura_data(index: int, lote_id: int) -> dict:
    return {
        "codigo_lectura": f"SEED-TEMP-{index:04d}",
        "lote_id": lote_id,
        "ubicacion_almacen": "Almacen de prueba",
        "temperatura_registrada": 20.0,
        "estado_lectura": "normal",
    }


def reporte_data(index: int, lote_id: int) -> dict:
    return {
        "codigo_reporte": f"SEED-REP-{index:04d}",
        "lote_id": lote_id,
        "tipo_reporte": "inventario_prueba",
        "destinatario": "auditoria@example.com",
        "contenido": f"Reporte de prueba {index:04d}",
    }
