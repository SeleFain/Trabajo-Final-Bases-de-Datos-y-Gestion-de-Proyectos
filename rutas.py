from flask import Blueprint, jsonify, render_template, request
from decimal import Decimal, InvalidOperation
from textwrap import dedent
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from extensiones import db

web_bp = Blueprint("web", __name__)

# Lista cerrada: el frontend no puede enviar nombres arbitrarios de tablas o SQL.
TABLAS_PERMITIDAS = {
    "clientes": "Clientes",
    "categorias": "Categorías",
    "subcategorias": "Subcategorías",
    "productos": "Productos",
    "modos_envio": "Modos de envío",
    "pedidos": "Pedidos",
    "detalle_pedido": "Detalle de pedidos",
    "Superstore": "Datos originales (Superstore)",
}

REPORTES = {
    "ventas_categoria": {
        "titulo": "Ventas por categoría",
        "descripcion": "Ventas, ganancias y unidades agrupadas por categoría.",
        "sql": """
            SELECT c.categoria,
                   COUNT(*) AS lineas_vendidas,
                   SUM(d.cantidad) AS unidades_vendidas,
                   ROUND(SUM(d.ventas), 2) AS ventas_totales,
                   ROUND(SUM(d.ganancia), 2) AS ganancia_total
            FROM detalle_pedido d
            JOIN productos p ON p.id_producto = d.id_producto
            JOIN subcategorias sc ON sc.id_subcategoria = p.id_subcategoria
            JOIN categorias c ON c.id_categoria = sc.id_categoria
            GROUP BY c.id_categoria, c.categoria
            ORDER BY ventas_totales DESC
        """,
    },
    "ventas_region": {
        "titulo": "Ventas por región",
        "descripcion": "Pedidos, unidades, ventas y ganancias por región.",
        "sql": """
            SELECT p.region,
                   COUNT(DISTINCT p.id_pedido) AS cantidad_pedidos,
                   SUM(d.cantidad) AS unidades_vendidas,
                   ROUND(SUM(d.ventas), 2) AS ventas_totales,
                   ROUND(SUM(d.ganancia), 2) AS ganancia_total
            FROM pedidos p
            JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
            GROUP BY p.region
            ORDER BY ventas_totales DESC
        """,
    },
    "top_clientes": {
        "titulo": "Principales clientes",
        "descripcion": "Los 10 clientes con mayor importe de ventas.",
        "sql": """
            SELECT c.id_cliente, c.nombre_cliente, c.segmento,
                   COUNT(DISTINCT p.id_pedido) AS cantidad_pedidos,
                   ROUND(SUM(d.ventas), 2) AS ventas_totales
            FROM clientes c
            JOIN pedidos p ON p.id_cliente = c.id_cliente
            JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
            GROUP BY c.id_cliente, c.nombre_cliente, c.segmento
            ORDER BY ventas_totales DESC
            LIMIT 10
        """,
    },
    "productos_vendidos": {
        "titulo": "Productos más vendidos",
        "descripcion": "Los 10 productos con más unidades vendidas.",
        "sql": """
            SELECT p.id_producto, p.codigo_producto, p.nombre_producto,
                   c.categoria, sc.subcategoria,
                   SUM(d.cantidad) AS unidades_vendidas,
                   ROUND(SUM(d.ventas), 2) AS ventas_totales,
                   ROUND(SUM(d.ganancia), 2) AS ganancia_total
            FROM detalle_pedido d
            JOIN productos p ON p.id_producto = d.id_producto
            JOIN subcategorias sc ON sc.id_subcategoria = p.id_subcategoria
            JOIN categorias c ON c.id_categoria = sc.id_categoria
            GROUP BY p.id_producto, p.codigo_producto, p.nombre_producto,
                     c.categoria, sc.subcategoria
            ORDER BY unidades_vendidas DESC
            LIMIT 10
        """,
    },
    "pedidos_segmento": {
        "titulo": "Pedidos por segmento",
        "descripcion": "Cantidad de pedidos y ventas según el segmento de cliente.",
        "sql": """
            SELECT c.segmento,
                   COUNT(DISTINCT p.id_pedido) AS cantidad_pedidos,
                   ROUND(SUM(d.ventas), 2) AS ventas_totales
            FROM clientes c
            JOIN pedidos p ON p.id_cliente = c.id_cliente
            JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
            GROUP BY c.segmento
            ORDER BY ventas_totales DESC
        """,
    },
}

# Campos disponibles para buscar y orden de cada reporte: lista cerrada.
FILTROS_REPORTES = {
    "ventas_categoria": (["categoria"], "ventas_totales"),
    "ventas_region": (["region"], "ventas_totales"),
    "top_clientes": (["nombre_cliente", "id_cliente", "segmento"], "ventas_totales"),
    "productos_vendidos": (["nombre_producto", "codigo_producto", "categoria", "subcategoria"], "unidades_vendidas"),
    "pedidos_segmento": (["segmento"], "ventas_totales"),
}

def preparar_reporte(reporte_id):
    campos, orden = FILTROS_REPORTES[reporte_id]
    campo = request.args.get("campo", campos[0])
    if campo not in campos:
        raise ValueError("El campo de búsqueda no está permitido para este reporte.")
    busqueda = request.args.get("busqueda", "").strip()
    if len(busqueda) > 150:
        raise ValueError("La búsqueda debe tener como máximo 150 caracteres.")
    try:
        limite = int(request.args.get("limite", "10" if reporte_id in ("top_clientes", "productos_vendidos") else "100"))
        minimo = Decimal(request.args.get("min_ventas", "").strip() or "0")
    except (ValueError, InvalidOperation):
        raise ValueError("Ingresá una cantidad de resultados y ventas mínimas válidas.")
    if not 1 <= limite <= 100 or not minimo.is_finite() or minimo < 0 or minimo > Decimal("999999999999.99"):
        raise ValueError("Resultados: entre 1 y 100. Ventas mínimas: entre 0 y 999999999999.99.")
    # Quitamos el orden y el límite originales para filtrar ANTES de elegir el top.
    base = dedent(REPORTES[reporte_id]["sql"]).strip().split("ORDER BY")[0].strip()
    condiciones = ["ventas_totales >= :min_ventas"]
    parametros = {"min_ventas": float(minimo), "limite": limite}
    if busqueda:
        # Búsqueda literal: %, _ y ! se escapan; el valor siempre se parametriza.
        literal = busqueda.replace("!", "!!").replace("%", "!%").replace("_", "!_")
        condiciones.append(f"LOWER({campo}) LIKE LOWER(:busqueda) ESCAPE '!' ")
        parametros["busqueda"] = f"%{literal}%"
    sql = ("SELECT *\nFROM (\n" + base + "\n) AS resumen\nWHERE "
           + "\n  AND ".join(condiciones)
           + f"\nORDER BY {orden} DESC, {campos[0]} ASC\nLIMIT :limite")
    return sql, parametros

def ejecutar_consulta(sql, params=None):
    result = db.session.execute(text(sql), params or {})
    columnas = list(result.keys())
    filas = [dict(zip(columnas, fila)) for fila in result.fetchall()]
    # Valores numéricos/fechas pueden ser tipos que jsonify no serializa en todas las versiones.
    for fila in filas:
        for clave, valor in fila.items():
            if hasattr(valor, "isoformat"):
                fila[clave] = valor.isoformat()
            elif valor is not None and not isinstance(valor, (str, int, float, bool)):
                fila[clave] = float(valor) if hasattr(valor, "__float__") else str(valor)
    return columnas, filas

@web_bp.get("/")
def index():
    return render_template("index.html")

@web_bp.get("/api/tablas")
def listar_tablas():
    return jsonify([{"nombre": nombre, "etiqueta": etiqueta}
                    for nombre, etiqueta in TABLAS_PERMITIDAS.items()])

@web_bp.get("/api/tablas/<nombre>")
def obtener_tabla(nombre):
    if nombre not in TABLAS_PERMITIDAS:
        return jsonify({"error": "Tabla no permitida."}), 404
    try:
        # Identificador solo se usa después de validarse contra la lista cerrada.
        limite = 100
        columnas, filas = ejecutar_consulta(f"SELECT * FROM `{nombre}` LIMIT {limite}")
        total = db.session.execute(text(f"SELECT COUNT(*) FROM `{nombre}`")).scalar_one()
        return jsonify({"nombre": nombre, "etiqueta": TABLAS_PERMITIDAS[nombre],
                        "columnas": columnas, "filas": filas, "total": total,
                        "limite": limite})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "No se pudo leer la tabla. Verificá que exista en la base."}), 500

@web_bp.get("/api/indicadores")
def indicadores():
    try:
        sql = """
            SELECT
              (SELECT COUNT(*) FROM clientes) AS total_clientes,
              (SELECT COUNT(*) FROM pedidos) AS total_pedidos,
              (SELECT COUNT(*) FROM productos) AS total_productos,
              (SELECT COALESCE(SUM(ventas), 0) FROM detalle_pedido) AS ventas_totales,
              (SELECT COALESCE(SUM(ganancia), 0) FROM detalle_pedido) AS ganancia_total,
              (SELECT COALESCE(SUM(cantidad), 0) FROM detalle_pedido) AS unidades_vendidas
        """
        _, filas = ejecutar_consulta(sql)
        return jsonify(filas[0])
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "No se pudieron cargar los indicadores. Verificá el esquema de la base."}), 500

@web_bp.get("/api/reportes")
def listar_reportes():
    return jsonify([{"id": clave, "titulo": valor["titulo"],
                     "descripcion": valor["descripcion"], "campos": FILTROS_REPORTES[clave][0]}
                    for clave, valor in REPORTES.items()])

@web_bp.get("/api/reportes/<reporte_id>")
def obtener_reporte(reporte_id):
    reporte = REPORTES.get(reporte_id)
    if reporte is None:
        return jsonify({"error": "Reporte no encontrado."}), 404
    try:
        sql, parametros = preparar_reporte(reporte_id)
        columnas, filas = ejecutar_consulta(sql, parametros)
        return jsonify({"id": reporte_id, "titulo": reporte["titulo"],
                        "descripcion": reporte["descripcion"],
                        "columnas": columnas, "filas": filas,
                        "sql": sql, "parametros": parametros})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "No se pudo ejecutar el reporte. Revisá que las tablas y columnas coincidan con el README."}), 500
