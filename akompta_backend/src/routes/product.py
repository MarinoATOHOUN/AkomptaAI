from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.product import Product
from src.models.stock_movement import StockMovement
from src.routes.auth import verify_token

product_bp = Blueprint('product', __name__)

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

@product_bp.route('', methods=['GET'])
def get_products():
    """Récupère tous les produits de l'utilisateur"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        products = Product.query.filter_by(user_id=user.id).all()
        return jsonify([product.to_dict() for product in products]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('', methods=['POST'])
def create_product():
    """Crée un nouveau produit"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=float(data['price']),
            stock_quantity=int(data.get('stock_quantity', 0)),
            min_stock_threshold=int(data.get('min_stock_threshold', 5)),
            image_url=data.get('image_url'),
            category=data.get('category'),
            user_id=user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Créer un mouvement de stock initial si nécessaire
        if product.stock_quantity > 0:
            stock_movement = StockMovement(
                product_id=product.id,
                user_id=user.id,
                movement_type='in',
                quantity=product.stock_quantity,
                previous_stock=0,
                new_stock=product.stock_quantity,
                reason='initial_stock',
                notes='Stock initial lors de la création du produit'
            )
            db.session.add(stock_movement)
            db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Récupère un produit spécifique"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        product = Product.query.filter_by(id=product_id, user_id=user.id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Met à jour un produit"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        product = Product.query.filter_by(id=product_id, user_id=user.id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Mettre à jour les champs
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = float(data['price'])
        if 'min_stock_threshold' in data:
            product.min_stock_threshold = int(data['min_stock_threshold'])
        if 'image_url' in data:
            product.image_url = data['image_url']
        if 'category' in data:
            product.category = data['category']
        
        # Gérer les changements de stock
        if 'stock_quantity' in data:
            new_stock = int(data['stock_quantity'])
            if new_stock != product.stock_quantity:
                # Créer un mouvement de stock
                movement_type = 'in' if new_stock > product.stock_quantity else 'out'
                quantity = abs(new_stock - product.stock_quantity)
                
                stock_movement = StockMovement(
                    product_id=product.id,
                    user_id=user.id,
                    movement_type=movement_type,
                    quantity=quantity,
                    previous_stock=product.stock_quantity,
                    new_stock=new_stock,
                    reason='manual_adjustment',
                    notes=data.get('stock_notes', 'Ajustement manuel du stock')
                )
                db.session.add(stock_movement)
                
                product.stock_quantity = new_stock
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Supprime un produit"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        product = Product.query.filter_by(id=product_id, user_id=user.id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/low-stock', methods=['GET'])
def get_low_stock_products():
    """Récupère les produits avec un stock faible"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        products = Product.query.filter(
            Product.user_id == user.id,
            Product.stock_quantity <= Product.min_stock_threshold
        ).all()
        
        return jsonify([product.to_dict() for product in products]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/<int:product_id>/stock', methods=['POST'])
def update_stock(product_id):
    """Met à jour le stock d'un produit"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        product = Product.query.filter_by(id=product_id, user_id=user.id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        if 'quantity' not in data or 'movement_type' not in data:
            return jsonify({'error': 'quantity and movement_type are required'}), 400
        
        quantity = int(data['quantity'])
        movement_type = data['movement_type']  # 'in' ou 'out'
        
        if movement_type not in ['in', 'out']:
            return jsonify({'error': 'movement_type must be "in" or "out"'}), 400
        
        previous_stock = product.stock_quantity
        
        if movement_type == 'in':
            new_stock = previous_stock + quantity
        else:
            new_stock = max(0, previous_stock - quantity)
        
        # Créer le mouvement de stock
        stock_movement = StockMovement(
            product_id=product.id,
            user_id=user.id,
            movement_type=movement_type,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reason=data.get('reason', 'manual_adjustment'),
            notes=data.get('notes'),
            voice_command=data.get('voice_command')
        )
        
        product.stock_quantity = new_stock
        
        db.session.add(stock_movement)
        db.session.commit()
        
        return jsonify({
            'message': 'Stock updated successfully',
            'product': product.to_dict(),
            'movement': stock_movement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

