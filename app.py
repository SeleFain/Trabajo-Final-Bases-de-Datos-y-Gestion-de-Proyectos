from flask import Flask
from config import Config
from extensiones import db
from rutas import web_bp
# Importamos modelos para que db.create_all() sepa qué tablas crear
import modelos 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Vinculamos la base de datos a la aplicación de Flask
    db.init_app(app)
    
    # Registramos el Blueprint de nuestras rutas
    app.register_blueprint(web_bp)
    
    # Creamos las tablas en MySQL automáticamente al arrancar la app
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
