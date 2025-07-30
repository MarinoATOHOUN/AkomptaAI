from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.user import db
from src.models.savings import Savings
from src.routes.auth import verify_token

savings_bp = Blueprint('savings', __name__)

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

@savings_bp.route('', methods=['GET'])
def get_savings():
    """Récupère toutes les transactions d'épargne de l'utilisateur"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Paramètres de filtrage
        transaction_type = request.args.get('type')  # deposit, withdrawal
        status = request.args.get('status')  # pending, completed, failed
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Construire la requête de base
        query = Savings.query.filter_by(user_id=user.id)
        
        # Filtrer par type de transaction
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        # Filtrer par statut
        if status:
            query = query.filter_by(status=status)
        
        # Ordonner par date décroissante
        query = query.order_by(Savings.transaction_date.desc())
        
        # Pagination
        savings = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'savings': [saving.to_dict() for saving in savings.items],
            'total': savings.total,
            'pages': savings.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@savings_bp.route('', methods=['POST'])
def create_savings_transaction():
    """Crée une nouvelle transaction d'épargne"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['amount', 'transaction_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        if data['transaction_type'] not in ['deposit', 'withdrawal']:
            return jsonify({'error': 'transaction_type must be "deposit" or "withdrawal"'}), 400
        
        savings = Savings(
            user_id=user.id,
            amount=float(data['amount']),
            transaction_type=data['transaction_type'],
            payment_method=data.get('payment_method', 'mobile_money'),
            mobile_money_provider=data.get('mobile_money_provider'),
            transaction_id=data.get('transaction_id'),
            status=data.get('status', 'pending'),
            notes=data.get('notes')
        )
        
        # Si une date spécifique est fournie
        if 'transaction_date' in data:
            savings.transaction_date = datetime.fromisoformat(data['transaction_date'])
        
        db.session.add(savings)
        db.session.commit()
        
        return jsonify({
            'message': 'Savings transaction created successfully',
            'savings': savings.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@savings_bp.route('/<int:savings_id>', methods=['GET'])
def get_savings_transaction(savings_id):
    """Récupère une transaction d'épargne spécifique"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        savings = Savings.query.filter_by(id=savings_id, user_id=user.id).first()
        if not savings:
            return jsonify({'error': 'Savings transaction not found'}), 404
        
        return jsonify(savings.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@savings_bp.route('/<int:savings_id>', methods=['PUT'])
def update_savings_transaction(savings_id):
    """Met à jour une transaction d'épargne (principalement le statut)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        savings = Savings.query.filter_by(id=savings_id, user_id=user.id).first()
        if not savings:
            return jsonify({'error': 'Savings transaction not found'}), 404
        
        data = request.get_json()
        
        # Mettre à jour les champs autorisés
        if 'status' in data:
            if data['status'] in ['pending', 'completed', 'failed']:
                savings.status = data['status']
        
        if 'transaction_id' in data:
            savings.transaction_id = data['transaction_id']
        
        if 'notes' in data:
            savings.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Savings transaction updated successfully',
            'savings': savings.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@savings_bp.route('/<int:savings_id>', methods=['DELETE'])
def delete_savings_transaction(savings_id):
    """Supprime une transaction d'épargne"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        savings = Savings.query.filter_by(id=savings_id, user_id=user.id).first()
        if not savings:
            return jsonify({'error': 'Savings transaction not found'}), 404
        
        # Ne permettre la suppression que des transactions en attente
        if savings.status == 'completed':
            return jsonify({'error': 'Cannot delete completed transaction'}), 400
        
        db.session.delete(savings)
        db.session.commit()
        
        return jsonify({'message': 'Savings transaction deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@savings_bp.route('/balance', methods=['GET'])
def get_savings_balance():
    """Récupère le solde d'épargne total"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Calculer le solde d'épargne
        completed_savings = Savings.query.filter_by(
            user_id=user.id,
            status='completed'
        ).all()
        
        total_deposits = sum(
            s.amount for s in completed_savings 
            if s.transaction_type == 'deposit'
        )
        
        total_withdrawals = sum(
            s.amount for s in completed_savings 
            if s.transaction_type == 'withdrawal'
        )
        
        balance = total_deposits - total_withdrawals
        
        # Transactions en attente
        pending_deposits = sum(
            s.amount for s in Savings.query.filter_by(
                user_id=user.id,
                transaction_type='deposit',
                status='pending'
            ).all()
        )
        
        pending_withdrawals = sum(
            s.amount for s in Savings.query.filter_by(
                user_id=user.id,
                transaction_type='withdrawal',
                status='pending'
            ).all()
        )
        
        return jsonify({
            'balance': balance,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'pending_deposits': pending_deposits,
            'pending_withdrawals': pending_withdrawals,
            'available_balance': balance - pending_withdrawals
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@savings_bp.route('/providers', methods=['GET'])
def get_mobile_money_providers():
    """Récupère la liste des fournisseurs Mobile Money disponibles"""
    providers = [
        {
            'id': 'mtn_momo',
            'name': 'MTN Mobile Money',
            'short_name': 'MTN MoMo',
            'color': '#FFCC00',
            'fees': {
                'deposit': 0.01,  # 1%
                'withdrawal': 0.015  # 1.5%
            }
        },
        {
            'id': 'orange_money',
            'name': 'Orange Money',
            'short_name': 'Orange Money',
            'color': '#FF6600',
            'fees': {
                'deposit': 0.01,
                'withdrawal': 0.015
            }
        },
        {
            'id': 'moov_money',
            'name': 'Moov Money',
            'short_name': 'Moov Money',
            'color': '#0066CC',
            'fees': {
                'deposit': 0.01,
                'withdrawal': 0.015
            }
        }
    ]
    
    return jsonify(providers), 200

@savings_bp.route('/stats', methods=['GET'])
def get_savings_stats():
    """Récupère les statistiques d'épargne"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        period = request.args.get('period', 'month')  # week, month, year
        
        # Définir la période
        if period == 'week':
            start_date = datetime.now() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.now() - timedelta(days=30)
        elif period == 'year':
            start_date = datetime.now() - timedelta(days=365)
        else:
            start_date = None
        
        # Construire la requête
        query = Savings.query.filter_by(user_id=user.id, status='completed')
        if start_date:
            query = query.filter(Savings.transaction_date >= start_date)
        
        savings = query.all()
        
        # Calculer les statistiques
        total_deposits = sum(s.amount for s in savings if s.transaction_type == 'deposit')
        total_withdrawals = sum(s.amount for s in savings if s.transaction_type == 'withdrawal')
        net_savings = total_deposits - total_withdrawals
        
        # Statistiques par fournisseur
        provider_stats = {}
        for saving in savings:
            provider = saving.mobile_money_provider or 'cash'
            if provider not in provider_stats:
                provider_stats[provider] = {
                    'deposits': 0,
                    'withdrawals': 0,
                    'count': 0
                }
            
            if saving.transaction_type == 'deposit':
                provider_stats[provider]['deposits'] += saving.amount
            else:
                provider_stats[provider]['withdrawals'] += saving.amount
            
            provider_stats[provider]['count'] += 1
        
        # Évolution de l'épargne (par jour)
        daily_savings = {}
        for saving in savings:
            date_key = saving.transaction_date.date().isoformat()
            if date_key not in daily_savings:
                daily_savings[date_key] = {'deposits': 0, 'withdrawals': 0}
            
            if saving.transaction_type == 'deposit':
                daily_savings[date_key]['deposits'] += saving.amount
            else:
                daily_savings[date_key]['withdrawals'] += saving.amount
        
        return jsonify({
            'period': period,
            'total_deposits': total_deposits,
            'total_withdrawals': total_withdrawals,
            'net_savings': net_savings,
            'transaction_count': len(savings),
            'provider_stats': provider_stats,
            'daily_savings': daily_savings
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

