from flask import request, jsonify
from app import app
import jwt
from functools import wraps
from flask_cors import CORS, cross_origin
from decouple import config 

SECRET_KEY = config('SECRET_KEY')

def jwt_required(f):
    @cross_origin()
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token faltante'}), 401

        token = token.split(" ")[1]
        print(token)
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])  # Corrige esta línea
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401

        return f(data, *args, **kwargs)

    return decorated
