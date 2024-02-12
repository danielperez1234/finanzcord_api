from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from api.models.user import User
from app import db
from decouple import config
import jwt

user_bp = Blueprint("user", __name__)
SECRET_KEY = config("SECRET_KEY")

from api.middleware.middleware import jwt_required


@user_bp.route("/", methods=["POST"])
@jwt_required
def registro():
    """
    Registrar un Nuevo Usuario
    ---
    parameters:
      - name: data
        in: body
        required: true
        description: Datos del usuario a registrar.
        schema:
          type: object
          properties:
            name:
              type: string
              description: Nombre del usuario.
            password:
              type: string
              description: Contraseña del usuario.
            email:
              type: string
              description: Correo electrónico del usuario.

    responses:
      200:
        description: Usuario registrado exitosamente.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de éxito.

      401:
        description: Acceso no autorizado.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de error.

    """
    try:
      data = request.get_json()
      name = data["name"]
      password = data["password"]
      email = data["email"]

      # Hashea la contraseña antes de almacenarla en la base de datos con el método 'pbkdf2:sha256'
      hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

      new_user = User(name=name, password=hashed_password, email=email)
      db.session.add(new_user)
      db.session.commit()

      return jsonify({"message": "Usuario registrado exitosamente"})
    except Exception as e:
      return jsonify({"error": "Error al crear el usuario: " + str(e)}), 500

@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required
def update_user(data, user_id):
    """
    Actualizar Datos de Usuario
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: iduser del usuario a actualizar.

    responses:
      200:
        description: Actualización exitosa.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de éxito.
            user_id:
              type: integer
              description: iduser del usuario actualizado.
            name:
              type: string
              description: Nuevo nombre del usuario.

      401:
        description: Acceso no autorizado.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de error.

      404:
        description: Usuario no encontrado.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de error.

    """
    new_data = request.get_json()
    
    # Verifica si el usuario existe
    user = User.query.filter_by(iduser=user_id).first()
    # verificacion de token
    token = request.headers.get('Authorization').split(' ')[1]
    tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    print(tokenDe)
    if not user:
      return jsonify({"message": "Usuario no encontrado"}), 404
    if user.email != tokenDe['email']:
      return jsonify({"message": "Este no es su usuario."}), 403
      
    # Actualiza la información del usuario
    if "name" in new_data:
        user.name = new_data["name"]
    if "password" in new_data:
        hashed_password = generate_password_hash(
            new_data["password"], method="pbkdf2:sha256"
        )
        user.password = hashed_password
    if "email" in new_data:
        user.email = new_data["email"]

    db.session.commit()

    return jsonify({"message": "Información del usuario actualizada exitosamente"})
    user_id = data["user_id"]  # Obtiene el iduser del usuario del token JWT
    new_data = request.get_json()

    # Verifica si el usuario existe
    user = User.query.filter_by(iduser=user_id).first()

    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Actualiza la información del usuario
    if "name" in new_data:
        user.name = new_data["name"]
    if "password" in new_data:
        hashed_password = generate_password_hash(
            new_data["password"], method="pbkdf2:sha256"
        )
        user.password = hashed_password
    if "email" in new_data:
        user.email = new_data["email"]

    db.session.commit()

    return jsonify({"message": "Información del usuario actualizada exitosamente"})


@user_bp.route("/login", methods=["POST"])
def login():
    """
    Iniciar Sesión de Usuario
    ---
    parameters:
      - name: data
        in: body
        required: true
        description: Credenciales de inicio de sesión.
        schema:
          type: object
          properties:
            email:
              type: string
              description: Correo electrónico del usuario.
            password:
              type: string
              description: Contraseña del usuario.

    responses:
      200:
        description: Inicio de sesión exitoso.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de éxito.
            user_id:
              type: integer
              description: iduser del usuario.
            name:
              type: string
              description: Nombre del usuario.
            token:
              type: string
              description: Token JWT de autenticación.
            email:
              type: string
              description: El mismo email que me estan mandando.

      401:
        description: Credenciales inválidas.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de error.

    """
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # Genera un nuevo token JWT con el correo del usuario al iniciar sesión
        token = generate_token(email)
        return jsonify(
            {
                "message": "Inicio de sesión exitoso",
                "user_id": user.iduser,
                "name": user.name,
                "token": token,
                "email":email
            }
        )
    else:
        return jsonify({"message": "Credenciales inválidas"})


@user_bp.route("/", methods=["GET"])
@jwt_required
def list_users(data):
    """
    Listar todos los usuarios
    ---
    responses:
      200:
        description: Lista de usuarios.
        schema:
          type: array
          items:
            type: object
            properties:
              user_id:
                type: integer
                description: iduser del usuario.
              name:
                type: string
                description: Nombre del usuario.
              email:
                type: string
                description: Correo electrónico del usuario.
      401:
        description: Acceso no autorizado.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de error.
    """
    # Obtiene todos los usuarios de la base de datos
    users = User.query.all()

    # Crea una lista de diccionarios con la información de cada usuario
    user_list = []
    for user in users:
        user_info = {"user_id": user.iduser, "name": user.name, "email": user.email}
        user_list.append(user_info)

    return jsonify(user_list)


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required
def get_user_by_id(data, user_id):
    """
    Obtener un usuario por su iduser
    ---
    responses:
      200:
        description: Información del usuario.
        schema:
          type: object
          properties:
            user_id:
              type: integer
              description: iduser del usuario.
            name:
              type: string
              description: Nombre del usuario.
            email:
              type: string
              description: Correo electrónico del usuario.
            # Agrega otros campos del usuario según tus necesidades
      404:
        description: Usuario no encontrado.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Mensaje de error.
      500:
        description: Error en el servidor.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Mensaje de error."""
    try:
        # Obtener el usuario por su iduser
        user = User.query.get(user_id)

        if user is None:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Crear un diccionario con los datos del usuario
        user_info = {"user_id": user.iduser, "name": user.name, "email": user.email}

        return jsonify(user_info), 200

    except Exception as e:
        return jsonify({"error": "Error al obtener el usuario: " + str(e)}), 500


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required
def delete_user(data, user_id):
    """
    Eliminar un Usuario
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: iduser del usuario a eliminar.

    responses:
      200:
        description: Eliminación exitosa.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de éxito.

      401:
        description: Acceso no autorizado.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de error.

      404:
        description: Usuario no encontrado.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Mensaje de error.
    """
    try:
        # Verifica si el usuario existe
        user = User.query.get(user_id)
        # verificacion de token
        token = request.headers.get('Authorization').split(' ')[1]
        tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404
        if user.email != tokenDe['email']:
          return jsonify({"message": "Este no es su usuario."}), 403

        if user.iduser == 1:
            return jsonify({"message": "No se permite eliminar al admin"}), 403
        # Cambia el estado is_delete a True en lugar de borrar el usuario
        user.is_delete = True
        db.session.commit()

        return jsonify({"message": "Usuario eliminado exitosamente"})

    except Exception as e:
        return jsonify({"error": "Error al eliminar el usuario: " + str(e)}), 500


def generate_token(email):
    payload = {"email": email}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
