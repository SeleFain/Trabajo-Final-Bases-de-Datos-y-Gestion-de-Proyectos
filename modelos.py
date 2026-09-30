from extensiones import db
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class Cliente(db.Model):
    __tablename__ = "clientes"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=True)