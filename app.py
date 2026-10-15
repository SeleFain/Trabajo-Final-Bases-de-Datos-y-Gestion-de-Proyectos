from flask import Flask
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from config import Config
from extensiones import db
from rutas import web_bp
<<<<<<< HEAD
=======

import modelos 
>>>>>>> 93fea182cd05d5d9e0573b3739f451ec9770aec8

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
<<<<<<< HEAD
    db.init_app(app)
    app.register_blueprint(web_bp)

    @app.get("/api/estado")
    def estado():
        try:
            db.session.execute(text("SELECT 1"))
            return {"estado": "ok", "base_datos": app.config["BASE_DATOS"]}, 200
        except SQLAlchemyError:
            app.logger.exception("No se pudo comprobar la conexión a la base")
            return {"estado": "error", "mensaje": "No se pudo conectar con la base de datos."}, 503

=======
    
    
    db.init_app(app)
    
    
    app.register_blueprint(web_bp)
    
    
    with app.app_context():
        db.create_all()
        
>>>>>>> 93fea182cd05d5d9e0573b3739f451ec9770aec8
    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)

