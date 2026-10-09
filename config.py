import os

class Config:
    USUARIO = os.getenv("USUARIO", "root")
    PASSWORD = os.getenv("PASSWORD", "1234")
    # 'db' es el nombre del servicio en docker-compose; cae en 'localhost' si ejecutas fuera de Docker
    SERVIDOR = os.getenv("SERVIDOR", "localhost")
    PUERTO = os.getenv("PUERTO", "3306")
    BASE_DATOS = os.getenv("BASE_DATOS", "clientes_supermercado")
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USUARIO}:{PASSWORD}@{SERVIDOR}:{PUERTO}/{BASE_DATOS}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}