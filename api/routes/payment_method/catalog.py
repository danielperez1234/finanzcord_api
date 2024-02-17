from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from api.models.payment_method import PaymentMethod 
from api.models.user import User
from app import db
from decouple import config
import jwt

catalog_bp = Blueprint("catalog", __name__)
SECRET_KEY = config("SECRET_KEY")

from api.middleware.middleware import jwt_required

@catalog_bp.route("/", methods=["GET"])
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
    """
    payment_methods = filterPaymentMethodUser(request)
    
    payment_method_list = []

    for payment_method in payment_methods:
        payment_method_info = {
            "id": payment_method.id,
            "name": payment_method.name
        }
        payment_method_list.append(payment_method_info)

    return jsonify(payment_method_list)



def filterPaymentMethodUser(request):
  token = request.headers.get('Authorization').split(' ')[1]
  tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
  user = User.query.filter_by(email=tokenDe['email']).first()
    
  paymentMethod = PaymentMethod.query.filter_by(iduser=user.id, is_delete=0)
  return paymentMethod