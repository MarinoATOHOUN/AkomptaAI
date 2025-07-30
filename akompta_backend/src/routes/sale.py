from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.user import db
from src.models.sale import Sale
from src.models.product import Product
from src.models.stock_movement import StockMovement
from src.routes.auth import verify_token

sale_bp = Blueprint('sale', __name__)

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

@sale_bp.route('', methods=['GET'])
def get_sales():
    """Récupère toutes les ventes de l'utilisateur"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Paramètres de filtrage
        period = request.args.get('period', 'all')  # today, week, month, all
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Construire la requête de base
        query = Sale.query.filter_by(user_id=user.id)
        
        # Filtrer par période
        if period == 'today':
            today = datetime.now().date()
            query = query.filter(Sale.sale_date >= today)
        elif period == 'week':
            week_ago = datetime.now() - timedelta(days=7)
            query = query.filter(Sale.sale_date >= week_ago)
        elif period == 'month':
            month_ago = datetime.now() - timedelta(days=30)
            query = query.filter(Sale.sale_date >= month_ago)
        
        # Ordonner par date décroissante
        query = query.order_by(Sale.sale_date.desc())
        
        # Pagination
        sales = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'sales': [sale.to_dict() for sale in sales.items],
            'total': sales.total,
            'pages': sales.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sale_bp.route('', methods=['POST'])
def create_sale():
    """Crée une nouvelle vente"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['product_id', 'quantity', 'unit_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Vérifier que le produit existe et appartient à l'utilisateur
        product = Product.query.filter_by(id=data['product_id'], user_id=user.id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        quantity = int(data['quantity'])
        unit_price = float(data['unit_price'])
        total_amount = quantity * unit_price
        
        # Vérifier le stock disponible
        if product.stock_quantity < quantity:
            return jsonify({
                'error': f'Stock insuffisant. Stock disponible: {product.stock_quantity}'
            }), 400
        
        # Créer la vente
        sale = Sale(
            product_id=product.id,
            user_id=user.id,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            payment_method=data.get('payment_method', 'cash'),
            notes=data.get('notes'),
            voice_command=data.get('voice_command')
        )
        
        # Mettre à jour le stock du produit
        previous_stock = product.stock_quantity
        product.stock_quantity -= quantity
        
        # Créer le mouvement de stock
        stock_movement = StockMovement(
            product_id=product.id,
            user_id=user.id,
            movement_type='out',
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=product.stock_quantity,
            reason='sale',
            notes=f'Vente de {quantity} unités',
            voice_command=data.get('voice_command')
        )
        
        db.session.add(sale)
        db.session.add(stock_movement)
        db.session.commit()
        
        # Mettre à jour la référence du mouvement de stock
        stock_movement.reference_id = sale.id
        db.session.commit()
        
        return jsonify({
            'message': 'Sale created successfully',
            'sale': sale.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sale_bp.route('/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    """Récupère une vente spécifique"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        sale = Sale.query.filter_by(id=sale_id, user_id=user.id).first()
        if not sale:
            return jsonify({'error': 'Sale not found'}), 404
        
        return jsonify(sale.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sale_bp.route('/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    """Supprime une vente (et restaure le stock)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        sale = Sale.query.filter_by(id=sale_id, user_id=user.id).first()
        if not sale:
            return jsonify({'error': 'Sale not found'}), 404
        
        # Restaurer le stock
        product = Product.query.get(sale.product_id)
        if product:
            previous_stock = product.stock_quantity
            product.stock_quantity += sale.quantity
            
            # Créer un mouvement de stock pour la restauration
            stock_movement = StockMovement(
                product_id=product.id,
                user_id=user.id,
                movement_type='in',
                quantity=sale.quantity,
                previous_stock=previous_stock,
                new_stock=product.stock_quantity,
                reason='sale_cancellation',
                reference_id=sale.id,
                notes=f'Annulation de vente #{sale.id}'
            )
            db.session.add(stock_movement)
        
        db.session.delete(sale)
        db.session.commit()
        
        return jsonify({'message': 'Sale deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sale_bp.route('/stats', methods=['GET'])
def get_sales_stats():
    """Récupère les statistiques de ventes"""
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
        query = Sale.query.filter_by(user_id=user.id)
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        
        sales = query.all()
        
        # Calculer les statistiques
        total_sales = sum(sale.total_amount for sale in sales)
        total_quantity = sum(sale.quantity for sale in sales)
        total_transactions = len(sales)
        
        # Ventes par produit
        product_stats = {}
        for sale in sales:
            product_name = sale.product.name if sale.product else 'Produit supprimé'
            if product_name not in product_stats:
                product_stats[product_name] = {
                    'quantity': 0,
                    'amount': 0,
                    'transactions': 0
                }
            product_stats[product_name]['quantity'] += sale.quantity
            product_stats[product_name]['amount'] += sale.total_amount
            product_stats[product_name]['transactions'] += 1
        
        # Ventes par méthode de paiement
        payment_stats = {}
        for sale in sales:
            method = sale.payment_method
            if method not in payment_stats:
                payment_stats[method] = {'count': 0, 'amount': 0}
            payment_stats[method]['count'] += 1
            payment_stats[method]['amount'] += sale.total_amount
        
        return jsonify({
            'period': period,
            'total_sales': total_sales,
            'total_quantity': total_quantity,
            'total_transactions': total_transactions,
            'average_transaction': total_sales / total_transactions if total_transactions > 0 else 0,
            'product_stats': product_stats,
            'payment_stats': payment_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

