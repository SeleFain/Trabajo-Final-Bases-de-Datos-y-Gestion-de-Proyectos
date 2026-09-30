import os

class Config:
    # Cambia 'root', 'tu_password' y 'nombre_bd' por tus datos reales de MySQL
    USUARIO = "root"
    PASSWORD = "1234"
    SERVIDOR = "localhost"
    PUERTO = "3306"
    BASE_DATOS = "clientes_supermercado"
    
    # Combinamos todo usando el driver pymysql
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USUARIO}:{PASSWORD}@{SERVIDOR}:{PUERTO}/{BASE_DATOS}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Práctica recomendada para MySQL: evita que las conexiones inactivas mueran
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}