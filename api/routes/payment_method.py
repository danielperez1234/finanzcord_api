from flask import Blueprint, request, jsonify
from app import db
from api.models.payment_method import PaymentMethod
from api.models.user import User 
from api.middleware.middleware import jwt_required
import jwt
from decouple import config

payment_method_bp = Blueprint("payment_method", __name__)
SECRET_KEY = config("SECRET_KEY")


@payment_method_bp.route("/", methods=["GET"])
@jwt_required
def list_payment_methods(data):
    """
    List all payment methods
    ---
    responses:
      200:
        description: List of payment methods.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Payment method ID.
              name:
                type: string
                description: Name of the payment method.
              description:
                type: string
                description: Description of the payment method.
              created_at:
                type: string
                description: Timestamp when the payment method was created.
              updated_at:
                type: string
                description: Timestamp when the payment method was last updated.
    """
    payment_methods = filterPaymentMethodUser(request)
    
    payment_method_list = []

    for payment_method in payment_methods:
        payment_method_info = {
            "id": payment_method.id,
            "name": payment_method.name,
            "description": payment_method.description,
            "created_at": str(payment_method.created_at),
            "updated_at": str(payment_method.updated_at),
        }
        payment_method_list.append(payment_method_info)

    return jsonify(payment_method_list)


@payment_method_bp.route("/<int:payment_method_id>", methods=["GET"])
@jwt_required
def get_payment_method(data,payment_method_id):
    """
    Get payment method by ID
    ---
    parameters:
      - name: payment_method_id
        in: path
        type: integer
        required: true
        description: ID of the payment method to retrieve.

    responses:
      200:
        description: Information of the payment method.
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Payment method ID.
            name:
              type: string
              description: Name of the payment method.
            description:
              type: string
              description: Description of the payment method.
            created_at:
              type: string
              description: Timestamp when the payment method was created.
            updated_at:
              type: string
              description: Timestamp when the payment method was last updated.
      404:
        description: Payment method not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message.
    """
    token = request.headers.get('Authorization').split(' ')[1]
    tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    user = User.query.filter_by(email=tokenDe['email']).first()
    
    payment_method = PaymentMethod.query.get(payment_method_id)
    if payment_method.iduser != user.id:
        return jsonify({"error": "Metodo de pago ajeno"}), 403

    if not payment_method:
        return jsonify({"error": "Payment method not found"}), 404

    payment_method_info = {
        "id": payment_method.id,
        "name": payment_method.name,
        "description": payment_method.description,
        "created_at": str(payment_method.created_at),
        "updated_at": str(payment_method.updated_at),
    }

    return jsonify(payment_method_info), 200


@payment_method_bp.route("/", methods=["POST"])
@jwt_required
def create_payment_method(data):
    """
    Create a new payment method
    ---
    parameters:
      - name: data
        in: body
        required: true
        description: Data of the payment method to create.
        schema:
          type: object
          properties:
            name:
              type: string
              description: Name of the payment method.
            description:
              type: string
              description: Description of the payment method.

    responses:
      201:
        description: Payment method created successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
            id:
              type: integer
              description: ID of the created payment method.
      400:
        description: Bad request.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message.
    """
    try:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
        
        token = request.headers.get('Authorization').split(' ')[1]
        tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.filter_by(email=tokenDe['email']).first()
    
        new_payment_method = PaymentMethod(
            name=name, description=description, iduser=user.id
        )

        db.session.add(new_payment_method)
        db.session.commit()

        return jsonify({"message": "Payment method created successfully", "id": new_payment_method.id}), 201

    except Exception as e:
        return jsonify({"error": "Error creating payment method: " + str(e)}), 400


@payment_method_bp.route("/<int:payment_method_id>", methods=["PUT"])
@jwt_required
def update_payment_method(data,payment_method_id):
    """
    Update payment method by ID
    ---
    parameters:
      - name: payment_method_id
        in: path
        type: integer
        required: true
        description: ID of the payment method to update.
      - name: data
        in: body
        required: true
        description: Updated data for the payment method.
        schema:
          type: object
          properties:
            name:
              type: string
              description: Updated name of the payment method.
            description:
              type: string
              description: Updated description of the payment method.

    responses:
      200:
        description: Payment method updated successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
            id:
              type: integer
              description: ID of the updated payment method.
      404:
        description: Payment method not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message.
    """
    try:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")

        token = request.headers.get('Authorization').split(' ')[1]
        tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.filter_by(email=tokenDe['email']).first()
    
        payment_method = PaymentMethod.query.get(payment_method_id)
        if payment_method.iduser != user.id:
            return jsonify({"error": "Metodo de pago ajeno"}), 403

        if not payment_method:
            return jsonify({"error": "Payment method not found"}), 404

        payment_method.name = name if name is not None else payment_method.name
        payment_method.description = description if description is not None else payment_method.description

        db.session.commit()

        return jsonify({"message": "Payment method updated successfully", "id": payment_method.id}), 200

    except Exception as e:
        return jsonify({"error": "Error updating payment method: " + str(e)}), 500


@payment_method_bp.route("/<int:payment_method_id>", methods=["DELETE"])
@jwt_required
def delete_payment_method(data, payment_method_id):
    """
    Delete payment method by ID
    ---
    parameters:
      - name: payment_method_id
        in: path
        type: integer
        required: true
        description: ID of the payment method to delete.

    responses:
      200:
        description: Payment method deleted successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
      404:
        description: Payment method not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message.
    """
    try:
        
        
        token = request.headers.get('Authorization').split(' ')[1]
        tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.filter_by(email=tokenDe['email']).first()
    
        payment_method = PaymentMethod.query.get(payment_method_id)
        if payment_method.iduser != user.id:
            return jsonify({"error": "Metodo de pago ajeno"}), 403
        if not payment_method:
            return jsonify({"error": "Payment method not found"}), 404

        payment_method.is_delete = 1
        db.session.commit()

        return jsonify({"message": "Payment method deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Error deleting payment method: " + str(e)}), 500

def filterPaymentMethodUser(request):
  token = request.headers.get('Authorization').split(' ')[1]
  tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
  user = User.query.filter_by(email=tokenDe['email']).first()
    
  paymentMethod = PaymentMethod.query.filter_by(iduser=user.id, is_delete=0)
  return paymentMethod