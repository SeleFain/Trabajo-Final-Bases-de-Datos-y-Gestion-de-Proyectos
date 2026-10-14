from flask import Flask
from config import Config
from extensiones import db
from rutas import web_bp

import modelos 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    
    db.init_app(app)
    
    
    app.register_blueprint(web_bp)
    
    
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
