from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.user import db
from src.models.expense import Expense
from src.routes.auth import verify_token

expense_bp = Blueprint('expense', __name__)

def get_current_user():
    """Récupère l'utilisateur actuel à partir du token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    
    user_id = verify_token(token)
    if not user_id:
        return None
    
    from src.models.user import User
    return User.query.get(user_id)

@expense_bp.route('', methods=['GET'])
def get_expenses():
    """Récupère toutes les dépenses de l'utilisateur"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Paramètres de filtrage
        category = request.args.get('category')
        period = request.args.get('period', 'all')  # today, week, month, all
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Construire la requête de base
        query = Expense.query.filter_by(user_id=user.id)
        
        # Filtrer par catégorie
        if category and category != 'all':
            query = query.filter_by(category=category)
        
        # Filtrer par période
        if period == 'today':
            today = datetime.now().date()
            query = query.filter(Expense.expense_date >= today)
        elif period == 'week':
            week_ago = datetime.now() - timedelta(days=7)
            query = query.filter(Expense.expense_date >= week_ago)
        elif period == 'month':
            month_ago = datetime.now() - timedelta(days=30)
            query = query.filter(Expense.expense_date >= month_ago)
        
        # Ordonner par date décroissante
        query = query.order_by(Expense.expense_date.desc())
        
        # Pagination
        expenses = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'expenses': [expense.to_dict() for expense in expenses.items],
            'total': expenses.total,
            'pages': expenses.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('', methods=['POST'])
def create_expense():
    """Crée une nouvelle dépense"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['description', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        expense = Expense(
            user_id=user.id,
            description=data['description'],
            amount=float(data['amount']),
            category=data.get('category', 'autres'),
            payment_method=data.get('payment_method', 'cash'),
            receipt_url=data.get('receipt_url'),
            notes=data.get('notes'),
            voice_command=data.get('voice_command')
        )
        
        # Si une date spécifique est fournie
        if 'expense_date' in data:
            expense.expense_date = datetime.fromisoformat(data['expense_date'])
        
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({
            'message': 'Expense created successfully',
            'expense': expense.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """Récupère une dépense spécifique"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        return jsonify(expense.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Met à jour une dépense"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        data = request.get_json()
        
        # Mettre à jour les champs
        if 'description' in data:
            expense.description = data['description']
        if 'amount' in data:
            expense.amount = float(data['amount'])
        if 'category' in data:
            expense.category = data['category']
        if 'payment_method' in data:
            expense.payment_method = data['payment_method']
        if 'receipt_url' in data:
            expense.receipt_url = data['receipt_url']
        if 'notes' in data:
            expense.notes = data['notes']
        if 'expense_date' in data:
            expense.expense_date = datetime.fromisoformat(data['expense_date'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Expense updated successfully',
            'expense': expense.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Supprime une dépense"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        db.session.delete(expense)
        db.session.commit()
        
        return jsonify({'message': 'Expense deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expense_bp.route('/categories', methods=['GET'])
def get_categories():
    """Récupère les catégories de dépenses disponibles"""
    categories = [
        {'id': 'transport', 'name': 'Transport', 'color': 'blue'},
        {'id': 'achat_stock', 'name': 'Achat Stock', 'color': 'green'},
        {'id': 'equipement', 'name': 'Équipement', 'color': 'purple'},
        {'id': 'communication', 'name': 'Communication', 'color': 'orange'},
        {'id': 'marketing', 'name': 'Marketing', 'color': 'pink'},
        {'id': 'maintenance', 'name': 'Maintenance', 'color': 'yellow'},
        {'id': 'formation', 'name': 'Formation', 'color': 'indigo'},
        {'id': 'autres', 'name': 'Autres', 'color': 'gray'}
    ]
    
    return jsonify(categories), 200

@expense_bp.route('/stats', methods=['GET'])
def get_expense_stats():
    """Récupère les statistiques de dépenses"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        period = request.args.get('period', 'month')  # today, week, month, year
        
        # Définir la période
        if period == 'today':
            start_date = datetime.now().date()
        elif period == 'week':
            start_date = datetime.now() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.now() - timedelta(days=30)
        elif period == 'year':
            start_date = datetime.now() - timedelta(days=365)
        else:
            start_date = None
        
        # Construire la requête
        query = Expense.query.filter_by(user_id=user.id)
        if start_date:
            query = query.filter(Expense.expense_date >= start_date)
        
        expenses = query.all()
        
        # Calculer les statistiques
        total_expenses = sum(expense.amount for expense in expenses)
        total_transactions = len(expenses)
        
        # Dépenses par catégorie
        category_stats = {}
        for expense in expenses:
            category = expense.category
            if category not in category_stats:
                category_stats[category] = {'count': 0, 'amount': 0}
            category_stats[category]['count'] += 1
            category_stats[category]['amount'] += expense.amount
        
        # Dépenses par méthode de paiement
        payment_stats = {}
        for expense in expenses:
            method = expense.payment_method
            if method not in payment_stats:
                payment_stats[method] = {'count': 0, 'amount': 0}
            payment_stats[method]['count'] += 1
            payment_stats[method]['amount'] += expense.amount
        
        # Évolution des dépenses (par jour sur la période)
        daily_expenses = {}
        for expense in expenses:
            date_key = expense.expense_date.date().isoformat()
            if date_key not in daily_expenses:
                daily_expenses[date_key] = 0
            daily_expenses[date_key] += expense.amount
        
        return jsonify({
            'period': period,
            'total_expenses': total_expenses,
            'total_transactions': total_transactions,
            'average_transaction': total_expenses / total_transactions if total_transactions > 0 else 0,
            'category_stats': category_stats,
            'payment_stats': payment_stats,
            'daily_expenses': daily_expenses
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

