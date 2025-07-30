from flask import Blueprint, request, jsonify
import openai
import os
import json
import re
from src.models.user import db
from src.models.product import Product
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.stock_movement import StockMovement
from src.routes.auth import verify_token

voice_bp = Blueprint('voice', __name__)

# Configuration OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')
openai.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')

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

def transcribe_audio(audio_file):
    """Transcrit un fichier audio en texte"""
    try:
        # Utiliser OpenAI Whisper pour la transcription
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript.text
    except Exception as e:
        print(f"Erreur de transcription: {e}")
        return None

def parse_voice_command(text, user_id):
    """Parse une commande vocale et extrait les informations structurées"""
    try:
        # Récupérer les produits de l'utilisateur pour le contexte
        products = Product.query.filter_by(user_id=user_id).all()
        product_names = [p.name.lower() for p in products]
        
        prompt = f"""
        Tu es un assistant IA spécialisé dans l'analyse de commandes vocales pour un système de gestion commerciale.
        
        Produits disponibles: {', '.join(product_names)}
        
        Analyse cette commande vocale et extrait les informations structurées:
        "{text}"
        
        Réponds UNIQUEMENT avec un JSON valide dans ce format:
        {{
            "type": "sale|expense|stock_in|stock_out|unknown",
            "product": "nom du produit (si applicable)",
            "quantity": nombre (si applicable),
            "price": prix unitaire (si applicable),
            "total": montant total (si applicable),
            "description": "description de la transaction",
            "category": "catégorie (pour les dépenses)",
            "confidence": 0.0-1.0
        }}
        
        Types de commandes:
        - sale: "j'ai vendu", "vente de", "vendu"
        - expense: "dépense", "j'ai dépensé", "achat"
        - stock_in: "ajouter au stock", "réapprovisionner", "j'ai reçu"
        - stock_out: "retirer du stock", "perte", "cassé"
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Nettoyer le texte pour extraire le JSON
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group()
        
        return json.loads(result_text)
        
    except Exception as e:
        print(f"Erreur de parsing: {e}")
        return {
            "type": "unknown",
            "description": text,
            "confidence": 0.0
        }

def process_sale_command(data, user_id, voice_command):
    """Traite une commande de vente"""
    try:
        # Trouver le produit
        product = Product.query.filter(
            Product.user_id == user_id,
            Product.name.ilike(f"%{data['product']}%")
        ).first()
        
        if not product:
            return {"success": False, "error": f"Produit '{data['product']}' non trouvé"}
        
        quantity = data.get('quantity', 1)
        unit_price = data.get('price', product.price)
        total_amount = data.get('total', quantity * unit_price)
        
        # Vérifier le stock
        if product.stock_quantity < quantity:
            return {"success": False, "error": f"Stock insuffisant. Stock actuel: {product.stock_quantity}"}
        
        # Créer la vente
        sale = Sale(
            product_id=product.id,
            user_id=user_id,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            voice_command=voice_command
        )
        
        # Mettre à jour le stock
        previous_stock = product.stock_quantity
        product.stock_quantity -= quantity
        
        # Créer le mouvement de stock
        stock_movement = StockMovement(
            product_id=product.id,
            user_id=user_id,
            movement_type='out',
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=product.stock_quantity,
            reason='sale',
            reference_id=sale.id,
            voice_command=voice_command
        )
        
        db.session.add(sale)
        db.session.add(stock_movement)
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Vente enregistrée: {quantity} {product.name} pour {total_amount} FCFA",
            "sale": sale.to_dict()
        }
        
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}

def process_expense_command(data, user_id, voice_command):
    """Traite une commande de dépense"""
    try:
        amount = data.get('total') or data.get('price', 0)
        description = data.get('description', voice_command)
        category = data.get('category', 'autres')
        
        expense = Expense(
            user_id=user_id,
            description=description,
            amount=amount,
            category=category,
            voice_command=voice_command
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Dépense enregistrée: {description} pour {amount} FCFA",
            "expense": expense.to_dict()
        }
        
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}

def process_stock_command(data, user_id, voice_command):
    """Traite une commande de stock"""
    try:
        # Trouver le produit
        product = Product.query.filter(
            Product.user_id == user_id,
            Product.name.ilike(f"%{data['product']}%")
        ).first()
        
        if not product:
            return {"success": False, "error": f"Produit '{data['product']}' non trouvé"}
        
        quantity = data.get('quantity', 1)
        movement_type = 'in' if data['type'] == 'stock_in' else 'out'
        
        previous_stock = product.stock_quantity
        
        if movement_type == 'in':
            new_stock = previous_stock + quantity
        else:
            new_stock = max(0, previous_stock - quantity)
        
        # Créer le mouvement de stock
        stock_movement = StockMovement(
            product_id=product.id,
            user_id=user_id,
            movement_type=movement_type,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reason='voice_command',
            voice_command=voice_command
        )
        
        product.stock_quantity = new_stock
        
        db.session.add(stock_movement)
        db.session.commit()
        
        action = "ajouté au" if movement_type == 'in' else "retiré du"
        return {
            "success": True,
            "message": f"Stock mis à jour: {quantity} {product.name} {action} stock",
            "movement": stock_movement.to_dict()
        }
        
    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}

@voice_bp.route('/process', methods=['POST'])
def process_voice_command():
    """Traite une commande vocale"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Vérifier si un fichier audio est fourni
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file is required'}), 400
        
        audio_file = request.files['audio']
        
        # Transcrire l'audio
        transcription = transcribe_audio(audio_file)
        if not transcription:
            return jsonify({'error': 'Failed to transcribe audio'}), 500
        
        # Parser la commande
        parsed_data = parse_voice_command(transcription, user.id)
        
        result = {
            'transcription': transcription,
            'parsed_data': parsed_data,
            'success': False
        }
        
        # Traiter selon le type de commande
        if parsed_data['type'] == 'sale':
            process_result = process_sale_command(parsed_data, user.id, transcription)
        elif parsed_data['type'] == 'expense':
            process_result = process_expense_command(parsed_data, user.id, transcription)
        elif parsed_data['type'] in ['stock_in', 'stock_out']:
            process_result = process_stock_command(parsed_data, user.id, transcription)
        else:
            process_result = {
                "success": False,
                "error": "Commande non reconnue. Essayez de reformuler."
            }
        
        result.update(process_result)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/test-parse', methods=['POST'])
def test_parse():
    """Teste le parsing d'une commande vocale (pour le développement)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        parsed_data = parse_voice_command(text, user.id)
        
        return jsonify({
            'text': text,
            'parsed_data': parsed_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

