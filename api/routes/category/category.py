from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from api.models.category import Category
from api.models.user import User
from app import db
from decouple import config
import jwt

category_bp = Blueprint("category", __name__)
SECRET_KEY = config("SECRET_KEY")

from api.middleware.middleware import jwt_required

from api.routes.category.catalog import catalog_bp
category_bp.register_blueprint(catalog_bp, url_prefix='/catalog')

@category_bp.route("/", methods=["GET"])
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
              relevance:
                type: string
                description: Relevance of the category.
              meta:
                type: string
                description: Meta information related to the category.
              created_at:
                type: string
                description: Timestamp when the category was created.
              updated_at:
                type: string
                description: Timestamp when the category was last updated.
    """
    # verificacion de token
    categories = filterCategoryUser(request)
    category_list = []
    
    for category in categories:
        category_info = {
            "id": category.id,
            "description": category.description,
            "relevance": category.relevance,
            "meta": category.meta,
            "created_at": str(category.created_at),
            "updated_at": str(category.updated_at),
        }
        category_list.append(category_info)

    return jsonify(category_list)


@category_bp.route("/<int:category_id>", methods=["GET"])
@jwt_required
def get_category(data,category_id):
    """
    Get category by ID
    ---
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
        description: ID of the category to retrieve.

    responses:
      200:
        description: Information of the category.
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Category ID.
            description:
              type: string
              description: Description of the category.
            relevance:
              type: string
              description: Relevance of the category.
            meta:
              type: string
              description: Meta information related to the category.
            created_at:
              type: string
              description: Timestamp when the category was created.
            updated_at:
              type: string
              description: Timestamp when the category was last updated.
      404:
        description: Category not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message.
    """
    category = Category.query.get(category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    category_info = {
        "id": category.id,
        "description": category.description,
        "relevance": category.relevance,
        "meta": category.meta,
        "created_at": str(category.created_at),
        "updated_at": str(category.updated_at),
    }

    return jsonify(category_info), 200


@category_bp.route("/", methods=["POST"])
@jwt_required
def create_category(date):
    """
    Create a new category
    ---
    parameters:
      - name: data
        in: body
        required: true
        description: Data of the category to create.
        schema:
          type: object
          properties:
            description:
              type: string
              description: Description of the category.
            relevance:
              type: string
              description: Relevance of the category.
            meta:
              type: string
              description: Meta information related to the category.

    responses:
      201:
        description: Category created successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
            id:
              type: integer
              description: ID of the created category.
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
        description = data.get("description")
        relevance = data.get("relevance")
        meta = data.get("meta")
        token = request.headers.get('Authorization').split(' ')[1]
        tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.filter_by(email=tokenDe['email']).first()
        new_category = Category(
            description=description, relevance=relevance, meta=meta, iduser=user.id, is_delete=0
        )

        db.session.add(new_category)
        db.session.commit()

        return jsonify({"message": "Category created successfully", "id": new_category.id}), 201

    except Exception as e:
        return jsonify({"error": "Error creating category: " + str(e)}), 400


@category_bp.route("/<int:category_id>", methods=["PUT"])
@jwt_required
def update_category(data,category_id):
    """
    Update category by ID
    ---
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
        description: ID of the category to update.
      - name: data
        in: body
        required: true
        description: Updated data for the category.
        schema:
          type: object
          properties:
            description:
              type: string
              description: Updated description of the category.
            relevance:
              type: string
              description: Updated relevance of the category.
            meta:
              type: string
              description: Updated meta information related to the category.

    responses:
      200:
        description: Category updated successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
            id:
              type: integer
              description: ID of the updated category.
      404:
        description: Category not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message.
    """
    try:
        data = request.get_json()
        description = data.get("description")
        relevance = data.get("relevance")
        meta = data.get("meta")

        token = request.headers.get('Authorization').split(' ')[1]
        tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.filter_by(email=tokenDe['email']).first()
    
        category = Category.query.get(category_id)
        if category.iduser != user.id:
            return jsonify({"error": "Category ajena"}), 403
        if not category:
            return jsonify({"error": "Category not found"}), 404

        category.description = description if description is not None else category.description
        category.relevance = relevance if relevance is not None else category.relevance
        category.meta = meta if meta is not None else category.meta

        db.session.commit()

        return jsonify({"message": "Category updated successfully", "id": category.id}), 200

    except Exception as e:
        return jsonify({"error": "Error updating category: " + str(e)}), 500


@category_bp.route("/<int:category_id>", methods=["DELETE"])
@jwt_required
def delete_category(data,category_id):
    """
    Delete category by ID
    ---
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
        description: ID of the category to delete.

    responses:
      200:
        description: Category deleted successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
      404:
        description: Category not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message.
    """
    try:
        category = Category.query.get(category_id)

        token = request.headers.get('Authorization').split(' ')[1]
        tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.filter_by(email=tokenDe['email']).first()
    
        category = Category.query.get(category_id)
        if category.iduser != user.id:
            return jsonify({"error": "Category ajena"}), 403

        if not category:
            return jsonify({"error": "Category not found"}), 404

        category.is_delete = 1
        db.session.commit()

        return jsonify({"message": "Category deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Error deleting category: " + str(e)}), 500

def filterCategoryUser(request):
  token = request.headers.get('Authorization').split(' ')[1]
  tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
  user = User.query.filter_by(email=tokenDe['email']).first()
    
  categories = Category.query.filter_by(iduser=user.id, is_delete=0)
  return categories