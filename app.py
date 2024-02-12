from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from decouple import config
from flasgger import Swagger  # Agrega la importación de Flasgger
import os

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.json.sort_keys = False
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:123456@127.0.0.1:3306/finanzcord'
SECRET_KEY = config('SECRET_KEY')
print(config('SQLALCHEMY_DATABASE_URI'))

swagger = Swagger(app)

db = SQLAlchemy(app)

# Importa las rutas de usuario
from api.routes.user import user_bp




# Registra las rutas de usuario
app.register_blueprint(user_bp, url_prefix='/user')



# Custom 404 error handler
@app.errorhandler(404)
def not_found_error(error):
   return jsonify({"messenge": "Ruta no encontrada."}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
