import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./farmaceutica.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def migrate_inventory_schema(database_engine=engine):
    inspector = inspect(database_engine)
    despacho_columns = {column["name"] for column in inspector.get_columns("despachos")}
    with database_engine.begin() as connection:
        if database_engine.dialect.name == "postgresql":
            datetime_columns = {
                "despachos": {"fecha_despacho", "fecha_recepcion"},
                "inspecciones_calidad": {"fecha_inspeccion"},
                "medicamentos": {"fecha_actualizacion"},
                "monitoreo_temperatura": {"fecha_hora"},
                "reportes": {"fecha"},
                "trazabilidad": {"fecha"},
            }
            for table_name, column_names in datetime_columns.items():
                for column in inspector.get_columns(table_name):
                    if column["name"] in column_names and getattr(column["type"], "timezone", False):
                        connection.execute(text(
                            f'ALTER TABLE "{table_name}" '
                            f'ALTER COLUMN "{column["name"]}" '
                            "TYPE TIMESTAMP WITHOUT TIME ZONE "
                            f'USING "{column["name"]}" AT TIME ZONE current_setting(\'TIMEZONE\')'
                        ))

        if "medicamento_id" not in despacho_columns:
            connection.execute(text(
                "ALTER TABLE despachos ADD COLUMN medicamento_id INTEGER "
                "REFERENCES medicamentos(id)"
            ))

        connection.execute(text(
            """
            INSERT INTO lote_productos (
                lote_id, medicamento_id, cantidad_recibida, cantidad_disponible
            )
            SELECT l.id, l.medicamento_id, l.cantidad_recibida, l.cantidad_disponible
            FROM lotes AS l
            WHERE NOT EXISTS (
                SELECT 1 FROM lote_productos AS lp WHERE lp.lote_id = l.id
            )
            """
        ))
        connection.execute(text(
            """
            UPDATE despachos
            SET medicamento_id = (
                SELECT l.medicamento_id FROM lotes AS l WHERE l.id = despachos.lote_id
            )
            WHERE medicamento_id IS NULL
            """
        ))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
