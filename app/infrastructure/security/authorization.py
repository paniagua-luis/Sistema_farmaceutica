from sqlalchemy.orm import Session

from app.infrastructure.database import SessionLocal
from app.infrastructure.models.role_model import PermissionModel, RoleModel
from app.infrastructure.models.usuario_model import UsuarioModel


ROLE_PERMISSIONS = {
    "administrador": {
        "medicamentos.gestionar",
        "proveedores.gestionar",
        "sucursales.gestionar",
        "lotes.gestionar",
        "calidad.gestionar",
        "despachos.gestionar",
        "temperatura.gestionar",
        "trazabilidad.consultar",
        "reportes.consultar",
    },
    "almacen": {
        "lotes.gestionar",
        "temperatura.gestionar",
        "trazabilidad.consultar",
        "reportes.consultar",
    },
    "personal_calidad": {
        "calidad.gestionar",
        "temperatura.gestionar",
        "trazabilidad.consultar",
        "reportes.consultar",
    },
    "personal_sucursal": {
        "despachos.gestionar",
    },
    "proveedor": {
        "lotes.gestionar",
    },
    "ente_regulador": {
        "trazabilidad.consultar",
        "reportes.consultar",
    },
}

LEGACY_ROLE_ALIASES = {
    "admin": "administrador",
    "administracion": "administrador",
    "calidad": "personal_calidad",
    "sucursal": "personal_sucursal",
    "regulador": "ente_regulador",
    "operador": "almacen",
}


def initialize_authorization() -> None:
    session = SessionLocal()
    try:
        for old_role, new_role in LEGACY_ROLE_ALIASES.items():
            session.query(UsuarioModel).filter(UsuarioModel.rol == old_role).update(
                {UsuarioModel.rol: new_role}, synchronize_session=False
            )
        session.query(RoleModel).filter(RoleModel.nombre.in_(LEGACY_ROLE_ALIASES)).delete(
            synchronize_session=False
        )

        permissions = {}
        for permission_name in sorted({permission for values in ROLE_PERMISSIONS.values() for permission in values}):
            permission = session.query(PermissionModel).filter_by(nombre=permission_name).first()
            if not permission:
                permission = PermissionModel(nombre=permission_name)
                session.add(permission)
                session.flush()
            permissions[permission_name] = permission

        for role_name, permission_names in ROLE_PERMISSIONS.items():
            role = session.query(RoleModel).filter_by(nombre=role_name).first()
            if not role:
                role = RoleModel(nombre=role_name)
                session.add(role)
                session.flush()
            role.permisos = [permissions[name] for name in sorted(permission_names)]

        session.commit()
    finally:
        session.close()
