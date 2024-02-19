from flask import Blueprint, request, jsonify
from api.models.category import Category
from api.models.payment_method import PaymentMethod
from app import db
from api.models.expense import Expense  # Assuming you have an Expense model
from api.middleware.middleware import jwt_required
from api.models.user import User
import jwt
from decouple import config

expense_bp = Blueprint("expense", __name__)
SECRET_KEY = config("SECRET_KEY")


@expense_bp.route("/page/<int:page>", methods=["GET"])
@jwt_required
def list_expenses(data, page):
    """
    List all expenses
    ---
    responses:
      200:
        description: List of expenses.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Expense ID.
              concept:
                type: string
                description: Concept of the expense.
              idcategory:
                type: integer
                description: Category ID of the expense.
              amount:
                type: float
                description: Amount of the expense.
              description:
                type: string
                description: Description of the expense.
              created_at:
                type: string
                description: Timestamp when the expense was created.
              updated_at:
                type: string
                description: Timestamp when the expense was last updated.
              date:
                type: string
                description: Date of the expense.
              idpayment:
                type: integer
                description: Payment method ID of the expense.
              priority:
                type: integer
                description: Priority of the expense.
    """
    expenses = filterExpenseUser(request, page)
    expense_list = []

    for expense in expenses:
        expense_info = {
            "id": expense.id,
            "concept": expense.concept,
            "idcategory": expense.idcategory,
            "amount": float(expense.amount),
            "description": expense.description,
            "created_at": str(expense.created_at),
            "updated_at": str(expense.updated_at),
            "date": str(expense.date),
            "idpayment": expense.idpayment,
            "priority": expense.priority,
        }
        expense_list.append(expense_info)

    return jsonify(expense_list)


@expense_bp.route("/page/<int:page>/last-page/<int:lastpage>", methods=["GET"])
@jwt_required
def list_expensesByPage(data, page, lastpage):
    """
    List all expenses
    ---
    responses:
      200:
        description: List of expenses.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Expense ID.
              concept:
                type: string
                description: Concept of the expense.
              idcategory:
                type: integer
                description: Category ID of the expense.
              amount:
                type: float
                description: Amount of the expense.
              description:
                type: string
                description: Description of the expense.
              created_at:
                type: string
                description: Timestamp when the expense was created.
              updated_at:
                type: string
                description: Timestamp when the expense was last updated.
              date:
                type: string
                description: Date of the expense.
              idpayment:
                type: integer
                description: Payment method ID of the expense.
              priority:
                type: integer
                description: Priority of the expense.
    """
    expenses = filterExpenseUserRange(request, page, lastpage)
    expense_list = []
    categories = filterCategoryUser(request)
    payments = filterPaymentMethodUser(request)
    for expense in expenses:
        print(expense.idpayment)
        payment = next(
            (obj for obj in payments if obj.id == expense.idpayment), None)
        category = next((obj for obj in categories if obj.id ==
                        expense.idcategory), None)
        expense_info = {
            "id": expense.id,
            "concept": expense.concept,
            "idcategory": expense.idcategory,
            "category": {
            "id": category.id,
            "description": category.description,
            "relevance": category.relevance,
            "meta": category.meta,
            "created_at": str(category.created_at),
            "updated_at": str(category.updated_at),
        },
            "amount": float(expense.amount),
            "description": expense.description,
            "created_at": str(expense.created_at),
            "updated_at": str(expense.updated_at),
            "date": str(expense.date),
            "idpayment": expense.idpayment,
            "payment": {
                "id": payment.id,
                "name": payment.name,
                "description": payment.description,
                "created_at": str(payment.created_at),
                "updated_at": str(payment.updated_at),
            },
            "priority": expense.priority,
        }
        expense_list.append(expense_info)

    return jsonify(expense_list)


@expense_bp.route("/<int:expense_id>", methods=["GET"])
@jwt_required
def get_expense(data, expense_id):
    """
    Get expense by ID
    ---
    parameters:
      - name: expense_id
        in: path
        type: integer
        required: true
        description: ID of the expense to retrieve.

    responses:
      200:
        description: Information of the expense.
        schema:
          type: object
          properties:
            id:
              type: integer
              description: Expense ID.
            concept:
              type: string
              description: Concept of the expense.
            idcategory:
              type: integer
              description: Category ID of the expense.
            amount:
              type: float
              description: Amount of the expense.
            description:
              type: string
              description: Description of the expense.
            created_at:
              type: string
              description: Timestamp when the expense was created.
            updated_at:
              type: string
              description: Timestamp when the expense was last updated.
            date:
              type: string
              description: Date of the expense.
            idpayment:
              type: integer
              description: Payment method ID of the expense.
            priority:
              type: integer
              description: Priority of the expense.
      404:
        description: Expense not found.
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

    expense = Expense.query.get(expense_id)
    if expense.iduser != user.id:
        return jsonify({"error": "Gasto ajeno"}), 403

    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    expense_info = {
        "id": expense.id,
        "concept": expense.concept,
        "idcategory": expense.idcategory,
        "amount": expense.amount,
        "description": expense.description,
        "created_at": str(expense.created_at),
        "updated_at": str(expense.updated_at),
        "date": str(expense.date),
        "idpayment": expense.idpayment,
        "priority": expense.priority,
    }

    return jsonify(expense_info), 200


@expense_bp.route("/", methods=["POST"])
@jwt_required
def create_expense(data):
    """
    Create a new expense
    ---
    parameters:
      - name: data
        in: body
        required: true
        description: Data of the expense to create.
        schema:
          type: object
          properties:
            concept:
              type: string
              description: Concept of the expense.
            idcategory:
              type: integer
              description: Category ID of the expense.
            amount:
              type: float
              description: Amount of the expense.
            description:
              type: string
              description: Description of the expense.
            date:
              type: string
              description: Date of the expense.
            idpayment:
              type: integer
              description: Payment method ID of the expense.
            priority:
              type: integer
              description: Priority of the expense.

    responses:
      201:
        description: Expense created successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
            id:
              type: integer
              description: ID of the created expense.
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
        token = request.headers.get('Authorization').split(' ')[1]
        tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.filter_by(email=tokenDe['email']).first()

        data = request.get_json()
        concept = data.get("concept")
        idcategory = data.get("idcategory")
        amount = data.get("amount")
        description = data.get("description")
        date = data.get("date")
        idpayment = data.get("idpayment")
        priority = data.get("priority")
        iduser = user.id

        new_expense = Expense(
            concept=concept,
            idcategory=idcategory,
            amount=amount,
            description=description,
            date=date,
            idpayment=idpayment,
            priority=priority,
            iduser=iduser
        )

        db.session.add(new_expense)
        db.session.commit()

        return jsonify({"message": "Expense created successfully", "id": new_expense.id}), 201

    except Exception as e:
        return jsonify({"error": "Error creating expense: " + str(e)}), 400


@expense_bp.route("/<int:expense_id>", methods=["PUT"])
@jwt_required
def update_expense(data, expense_id):
    """
    Update expense by ID
    ---
    parameters:
      - name: expense_id
        in: path
        type: integer
        required: true
        description: ID of the expense to update.
      - name: data
        in: body
        required: true
        description: Updated data for the expense.
        schema:
          type: object
          properties:
            concept:
              type: string
              description: Updated concept of the expense.
            idcategory:
              type: integer
              description: Updated category ID of the expense.
            amount:
              type: float
              description: Updated amount of the expense.
            description:
              type: string
              description: Updated description of the expense.
            date:
              type: string
              description: Updated date of the expense.
            idpayment:
              type: integer
              description: Updated payment method ID of the expense.
            priority:
              type: integer
              description: Updated priority of the expense.

    responses:
      200:
        description: Expense updated successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
            id:
              type: integer
              description: ID of the updated expense.
      404:
        description: Expense not found.
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message.
    """
    try:
        data = request.get_json()
        concept = data.get("concept")
        idcategory = data.get("idcategory")
        amount = data.get("amount")
        description = data.get("description")
        date = data.get("date")
        idpayment = data.get("idpayment")
        priority = data.get("priority")

        token = request.headers.get('Authorization').split(' ')[1]
        tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.filter_by(email=tokenDe['email']).first()

        expense = Expense.query.get(expense_id)
        if expense.iduser != user.id:
            return jsonify({"error": "Gasto ajeno"}), 403

        if not expense:
            return jsonify({"error": "Expense not found"}), 404

        expense.concept = concept if concept is not None else expense.concept
        expense.idcategory = idcategory if idcategory is not None else expense.idcategory
        expense.amount = amount if amount is not None else expense.amount
        expense.description = description if description is not None else expense.description
        expense.date = date if date is not None else expense.date
        expense.idpayment = idpayment if idpayment is not None else expense.idpayment
        expense.priority = priority if priority is not None else expense.priority

        db.session.commit()

        return jsonify({"message": "Expense updated successfully", "id": expense.id}), 200

    except Exception as e:
        return jsonify({"error": "Error updating expense: " + str(e)}), 500


@expense_bp.route("/<int:expense_id>", methods=["DELETE"])
@jwt_required
def delete_expense(data, expense_id):
    """
    Delete expense by ID
    ---
    parameters:
      - name: expense_id
        in: path
        type: integer
        required: true
        description: ID of the expense to delete.

    responses:
      200:
        description: Expense deleted successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
      404:
        description: Expense not found.
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

        expense = Expense.query.get(expense_id)
        if expense.iduser != user.id:
            return jsonify({"error": "Gasto ajeno"}), 403

        if not expense:
            return jsonify({"error": "Expense not found"}), 404

        db.session.delete(expense)
        db.session.commit()

        return jsonify({"message": "Expense deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Error deleting expense: " + str(e)}), 500


def filterExpenseUser(request, page):
    token = request.headers.get('Authorization').split(' ')[1]
    tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    user = User.query.filter_by(email=tokenDe['email']).first()
    per_page = 100
    expense = Expense.query.order_by(Expense.date.desc()).filter_by(
        iduser=user.id).paginate(page=page, per_page=per_page, error_out=False)
    return expense


def filterExpenseUserRange(request, page, lastpage):
    token = request.headers.get('Authorization').split(' ')[1]
    tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    user = User.query.filter_by(email=tokenDe['email']).first()
    per_page = 100 * lastpage - page + 1
    expense = Expense.query.order_by(Expense.date.desc()).filter_by(
        iduser=user.id).paginate(page=page, per_page=per_page, error_out=False)
    return expense


def filterCategoryUser(request):
  token = request.headers.get('Authorization').split(' ')[1]
  tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
  user = User.query.filter_by(email=tokenDe['email']).first()
    
  categories = Category.query.filter_by(iduser=user.id, is_delete=0)
  return categories


def filterPaymentMethodUser(request):
    token = request.headers.get('Authorization').split(' ')[1]
    tokenDe = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    user = User.query.filter_by(email=tokenDe['email']).first()

    paymentMethod = PaymentMethod.query.filter_by(iduser=user.id)
    return paymentMethod
