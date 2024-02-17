from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from api.models.category import Category
from api.models.user import User
from app import db
from decouple import config
import jwt

catalog_bp = Blueprint("catalog", __name__)
SECRET_KEY = config("SECRET_KEY")

from api.middleware.middleware import jwt_required


@catalog_bp.route("/", methods=["GET"])
@jwt_required
def list_categories(data):
    """
    List all categories
    ---
    responses:
      200:
        description: List of categories.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Category ID.
              description:
                type: string
                description: Description of the category.
    """
    # verificacion de token
    categories = filterCategoryUser(request)
    category_list = []
    
    for category in categories:
        category_info = {
            "id": category.id,
            "description": category.description,
        }
        category_list.append(category_info)

    return jsonify(category_list)


def filterCategoryUser(request):
  token = request.headers.get('Authorization').split(' ')[1]
  tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
  user = User.query.filter_by(email=tokenDe['email']).first()
    
  categories = Category.query.filter_by(iduser=user.id, is_delete=0)
  return categories