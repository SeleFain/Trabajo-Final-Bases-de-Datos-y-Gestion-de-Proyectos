import os
from urllib.parse import quote_plus

class Config:
    USUARIO = os.getenv("USUARIO", "superstore_lector")
    PASSWORD = os.getenv("PASSWORD", "cambiar_esta_clave")
    SERVIDOR = os.getenv("SERVIDOR", "localhost")
    PUERTO = os.getenv("PUERTO", "3308")
    BASE_DATOS = os.getenv("BASE_DATOS", "clientes_supermercado_completa")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{quote_plus(USUARIO)}:{quote_plus(PASSWORD)}"
        f"@{SERVIDOR}:{PUERTO}/{BASE_DATOS}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 1800}

