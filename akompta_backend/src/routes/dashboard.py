from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func
from src.models.user import db
from src.models.product import Product
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.savings import Savings
from src.routes.auth import verify_token

dashboard_bp = Blueprint('dashboard', __name__)

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

@dashboard_bp.route('', methods=['GET'])
def get_dashboard_data():
    """Récupère les données du dashboard"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        period = request.args.get('period', 'month')  # day, week, month, year
        
        # Définir les périodes
        now = datetime.now()
        if period == 'day':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            previous_start = start_date - timedelta(days=1)
            previous_end = start_date
        elif period == 'week':
            start_date = now - timedelta(days=7)
            previous_start = start_date - timedelta(days=7)
            previous_end = start_date
        elif period == 'month':
            start_date = now - timedelta(days=30)
            previous_start = start_date - timedelta(days=30)
            previous_end = start_date
        elif period == 'year':
            start_date = now - timedelta(days=365)
            previous_start = start_date - timedelta(days=365)
            previous_end = start_date
        else:
            start_date = None
            previous_start = None
            previous_end = None
        
        # Récupérer les données de base
        dashboard_data = {}
        
        # 1. Statistiques générales
        total_products = Product.query.filter_by(user_id=user.id).count()
        
        # Ventes
        sales_query = Sale.query.filter_by(user_id=user.id)
        if start_date:
            current_sales = sales_query.filter(Sale.sale_date >= start_date).all()
            if previous_start and previous_end:
                previous_sales = sales_query.filter(
                    Sale.sale_date >= previous_start,
                    Sale.sale_date < previous_end
                ).all()
            else:
                previous_sales = []
        else:
            current_sales = sales_query.all()
            previous_sales = []
        
        total_sales = sum(sale.total_amount for sale in current_sales)
        total_sales_quantity = sum(sale.quantity for sale in current_sales)
        previous_sales_amount = sum(sale.total_amount for sale in previous_sales)
        
        # Dépenses
        expenses_query = Expense.query.filter_by(user_id=user.id)
        if start_date:
            current_expenses = expenses_query.filter(Expense.expense_date >= start_date).all()
            if previous_start and previous_end:
                previous_expenses = expenses_query.filter(
                    Expense.expense_date >= previous_start,
                    Expense.expense_date < previous_end
                ).all()
            else:
                previous_expenses = []
        else:
            current_expenses = expenses_query.all()
            previous_expenses = []
        
        total_expenses = sum(expense.amount for expense in current_expenses)
        previous_expenses_amount = sum(expense.amount for expense in previous_expenses)
        
        # Épargne
        savings_query = Savings.query.filter_by(user_id=user.id, status='completed')
        completed_savings = savings_query.all()
        
        total_savings_deposits = sum(
            s.amount for s in completed_savings 
            if s.transaction_type == 'deposit'
        )
        total_savings_withdrawals = sum(
            s.amount for s in completed_savings 
            if s.transaction_type == 'withdrawal'
        )
        total_savings = total_savings_deposits - total_savings_withdrawals
        
        # Solde total (approximatif)
        total_balance = total_sales - total_expenses + total_savings
        
        # 2. Ventes récentes (5 dernières)
        recent_sales = Sale.query.filter_by(user_id=user.id)\
            .order_by(Sale.sale_date.desc())\
            .limit(5)\
            .all()
        
        # 3. Produits en stock faible
        low_stock_products = Product.query.filter(
            Product.user_id == user.id,
            Product.stock_quantity <= Product.min_stock_threshold
        ).all()
        
        # 4. Données pour les graphiques
        # Graphique des ventes par période
        sales_chart_data = []
        if period == 'month':
            # Diviser le mois en 3 périodes de 10 jours
            for i in range(3):
                period_start = start_date + timedelta(days=i*10)
                period_end = start_date + timedelta(days=(i+1)*10)
                
                period_sales = [s for s in current_sales 
                              if period_start <= s.sale_date < period_end]
                period_previous = [s for s in previous_sales 
                                 if period_start - timedelta(days=30) <= s.sale_date < period_end - timedelta(days=30)]
                
                sales_chart_data.append({
                    'period': f'{i*10+1}-{(i+1)*10}',
                    'current': sum(s.total_amount for s in period_sales),
                    'previous': sum(s.total_amount for s in period_previous)
                })
        else:
            # Pour les autres périodes, créer des segments appropriés
            sales_chart_data = [
                {
                    'period': 'Période actuelle',
                    'current': total_sales,
                    'previous': previous_sales_amount
                }
            ]
        
        # 5. Calculs de tendances
        sales_trend = 'up' if total_sales > previous_sales_amount else 'down' if total_sales < previous_sales_amount else 'stable'
        expenses_trend = 'up' if total_expenses > previous_expenses_amount else 'down' if total_expenses < previous_expenses_amount else 'stable'
        
        # Construire la réponse
        dashboard_data = {
            'period': period,
            'total_balance': total_balance,
            'total_sales': total_sales,
            'total_expenses': total_expenses,
            'total_savings': total_savings,
            'total_products': total_products,
            'net_profit': total_sales - total_expenses,
            
            # Tendances
            'sales_trend': sales_trend,
            'expenses_trend': expenses_trend,
            'sales_change_percent': ((total_sales - previous_sales_amount) / previous_sales_amount * 100) if previous_sales_amount > 0 else 0,
            'expenses_change_percent': ((total_expenses - previous_expenses_amount) / previous_expenses_amount * 100) if previous_expenses_amount > 0 else 0,
            
            # Données détaillées
            'recent_sales': [sale.to_dict() for sale in recent_sales],
            'low_stock_products': [product.to_dict() for product in low_stock_products],
            'sales_chart': sales_chart_data,
            
            # Statistiques supplémentaires
            'total_sales_quantity': total_sales_quantity,
            'average_sale_amount': total_sales / len(current_sales) if current_sales else 0,
            'sales_count': len(current_sales),
            'expenses_count': len(current_expenses),
            
            # Top produits vendus
            'top_products': get_top_selling_products(user.id, start_date),
            
            # Répartition des dépenses par catégorie
            'expense_categories': get_expense_categories_summary(user.id, start_date)
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_top_selling_products(user_id, start_date=None, limit=5):
    """Récupère les produits les plus vendus"""
    try:
        query = db.session.query(
            Product.name,
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.total_amount).label('total_amount'),
            func.count(Sale.id).label('sales_count')
        ).join(Sale).filter(
            Product.user_id == user_id
        )
        
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        
        results = query.group_by(Product.id)\
            .order_by(func.sum(Sale.total_amount).desc())\
            .limit(limit)\
            .all()
        
        return [
            {
                'name': result.name,
                'total_quantity': result.total_quantity,
                'total_amount': result.total_amount,
                'sales_count': result.sales_count
            }
            for result in results
        ]
        
    except Exception as e:
        print(f"Error getting top products: {e}")
        return []

def get_expense_categories_summary(user_id, start_date=None):
    """Récupère le résumé des dépenses par catégorie"""
    try:
        query = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('count')
        ).filter(Expense.user_id == user_id)
        
        if start_date:
            query = query.filter(Expense.expense_date >= start_date)
        
        results = query.group_by(Expense.category)\
            .order_by(func.sum(Expense.amount).desc())\
            .all()
        
        return [
            {
                'category': result.category,
                'total_amount': result.total_amount,
                'count': result.count
            }
            for result in results
        ]
        
    except Exception as e:
        print(f"Error getting expense categories: {e}")
        return []

@dashboard_bp.route('/summary', methods=['GET'])
def get_dashboard_summary():
    """Récupère un résumé rapide du dashboard"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Données de base
        total_products = Product.query.filter_by(user_id=user.id).count()
        low_stock_count = Product.query.filter(
            Product.user_id == user.id,
            Product.stock_quantity <= Product.min_stock_threshold
        ).count()
        
        # Ventes du jour
        today = datetime.now().date()
        today_sales = Sale.query.filter(
            Sale.user_id == user.id,
            Sale.sale_date >= today
        ).all()
        
        today_sales_amount = sum(sale.total_amount for sale in today_sales)
        today_sales_count = len(today_sales)
        
        # Dépenses du jour
        today_expenses = Expense.query.filter(
            Expense.user_id == user.id,
            Expense.expense_date >= today
        ).all()
        
        today_expenses_amount = sum(expense.amount for expense in today_expenses)
        
        return jsonify({
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'today_sales_amount': today_sales_amount,
            'today_sales_count': today_sales_count,
            'today_expenses_amount': today_expenses_amount,
            'today_profit': today_sales_amount - today_expenses_amount
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

