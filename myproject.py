from flask import Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy


from blueprints.spicy_sweet.routes import spicy_sweet
from blueprints.spicy_sweet.models import db

load_dotenv()

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False


db.init_app(app)

with app.app_context():
    db.create_all()


app.register_blueprint(spicy_sweet)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)