from flask import Blueprint, jsonify, request, render_template
from extensiones import db
from modelos import Cliente

# Creamos el Blueprint
web_bp = Blueprint("web", __name__)

# RUTA PARA MOSTRAR LA PÁGINA WEB
@web_bp.route("/")
def index():
    return render_template("index.html")


# RUTAS DE LA API (Para JavaScript)
@web_bp.route("/api/clientes", methods=["GET"])
def listar_clientes():
    stmt = db.select(Cliente)
    clientes = db.session.execute(stmt).scalars().all()
    resultado = [{"id": c.id, "nombre": c.nombre, "email": c.email, "telefono": c.telefono} for c in clientes]
    return jsonify(resultado), 200

@web_bp.route("/api/clientes", methods=["POST"])
def registrar_cliente():
    datos = request.get_json()
    if not datos or "nombre" not in datos or "email" not in datos:
        return jsonify({"error": "Nombre y email son obligatorios"}), 400
        
    try:
        nuevo_cliente = Cliente(
            nombre=datos["nombre"],
            email=datos["email"],
            telefono=datos.get("telefono")
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({"mensaje": "Cliente registrado exitosamente"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "El email ya está registrado"}), 400