import os
from urllib.parse import quote_plus

class Config:
<<<<<<< HEAD
    USUARIO = os.getenv("USUARIO", "root")
    PASSWORD = os.getenv("PASSWORD", "1234")
=======
    USUARIO = os.getenv("USUARIO", "root")
    PASSWORD = os.getenv("PASSWORD", "1234")
   
>>>>>>> 93fea182cd05d5d9e0573b3739f451ec9770aec8
    SERVIDOR = os.getenv("SERVIDOR", "localhost")
    PUERTO = os.getenv("PUERTO", "3308")
    BASE_DATOS = os.getenv("BASE_DATOS", "clientes_supermercado_completa")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{quote_plus(USUARIO)}:{quote_plus(PASSWORD)}"
        f"@{SERVIDOR}:{PUERTO}/{BASE_DATOS}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 1800}

