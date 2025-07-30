from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
import tempfile
from src.models.user import db
from src.models.report import Report
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.savings import Savings
from src.models.product import Product
from src.routes.auth import verify_token

report_bp = Blueprint('report', __name__)

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

@report_bp.route('', methods=['GET'])
def get_reports():
    """Récupère tous les rapports de l'utilisateur"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        reports = Report.query.filter_by(user_id=user.id)\
            .order_by(Report.generated_at.desc())\
            .all()
        
        return jsonify([report.to_dict() for report in reports]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/generate', methods=['POST'])
def generate_report():
    """Génère un nouveau rapport"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validation des données
        report_type = data.get('report_type', 'monthly')  # daily, weekly, monthly, annual
        
        if report_type not in ['daily', 'weekly', 'monthly', 'annual']:
            return jsonify({'error': 'Invalid report type'}), 400
        
        # Définir les dates de période
        end_date = datetime.now()
        
        if report_type == 'daily':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif report_type == 'weekly':
            start_date = end_date - timedelta(days=7)
        elif report_type == 'monthly':
            start_date = end_date - timedelta(days=30)
        elif report_type == 'annual':
            start_date = end_date - timedelta(days=365)
        
        # Récupérer les données pour le rapport
        sales = Sale.query.filter(
            Sale.user_id == user.id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date
        ).all()
        
        expenses = Expense.query.filter(
            Expense.user_id == user.id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).all()
        
        savings = Savings.query.filter(
            Savings.user_id == user.id,
            Savings.transaction_date >= start_date,
            Savings.transaction_date <= end_date,
            Savings.status == 'completed'
        ).all()
        
        # Calculer les totaux
        total_sales = sum(sale.total_amount for sale in sales)
        total_expenses = sum(expense.amount for expense in expenses)
        net_profit = total_sales - total_expenses
        
        total_savings_deposits = sum(s.amount for s in savings if s.transaction_type == 'deposit')
        total_savings_withdrawals = sum(s.amount for s in savings if s.transaction_type == 'withdrawal')
        net_savings = total_savings_deposits - total_savings_withdrawals
        
        # Créer l'enregistrement du rapport
        report = Report(
            user_id=user.id,
            report_type=report_type,
            report_period_start=start_date,
            report_period_end=end_date,
            total_sales=total_sales,
            total_expenses=total_expenses,
            net_profit=net_profit,
            total_savings=net_savings
        )
        
        # Générer le PDF
        pdf_path = generate_pdf_report(user, report, sales, expenses, savings)
        report.file_path = pdf_path
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Report generated successfully',
            'report': report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def generate_pdf_report(user, report, sales, expenses, savings):
    """Génère un rapport PDF"""
    try:
        # Créer un fichier temporaire
        temp_dir = tempfile.mkdtemp()
        filename = f"rapport_{report.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(temp_dir, filename)
        
        # Créer le document PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2D5A3D'),
            alignment=1  # Centré
        )
        
        # Titre du rapport
        title = f"Rapport {report.report_type.title()} - {user.business_name or user.username}"
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # Informations générales
        info_data = [
            ['Période:', f"{report.report_period_start.strftime('%d/%m/%Y')} - {report.report_period_end.strftime('%d/%m/%Y')}"],
            ['Généré le:', datetime.now().strftime('%d/%m/%Y à %H:%M')],
            ['Utilisateur:', user.username],
            ['Commerce:', user.business_name or 'Non spécifié']
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F5E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Résumé financier
        story.append(Paragraph("Résumé Financier", styles['Heading2']))
        
        summary_data = [
            ['Indicateur', 'Montant (FCFA)'],
            ['Total des Ventes', f"{report.total_sales:,.0f}"],
            ['Total des Dépenses', f"{report.total_expenses:,.0f}"],
            ['Bénéfice Net', f"{report.net_profit:,.0f}"],
            ['Épargne Nette', f"{report.total_savings:,.0f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5A3D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Détail des ventes
        if sales:
            story.append(Paragraph("Détail des Ventes", styles['Heading2']))
            
            sales_data = [['Date', 'Produit', 'Quantité', 'Prix Unit.', 'Total']]
            for sale in sales[:10]:  # Limiter à 10 ventes
                sales_data.append([
                    sale.sale_date.strftime('%d/%m'),
                    sale.product.name if sale.product else 'N/A',
                    str(sale.quantity),
                    f"{sale.unit_price:,.0f}",
                    f"{sale.total_amount:,.0f}"
                ])
            
            sales_table = Table(sales_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 1*inch])
            sales_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A8D5BA')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(sales_table)
            
            if len(sales) > 10:
                story.append(Paragraph(f"... et {len(sales) - 10} autres ventes", styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # Détail des dépenses
        if expenses:
            story.append(Paragraph("Détail des Dépenses", styles['Heading2']))
            
            expenses_data = [['Date', 'Description', 'Catégorie', 'Montant']]
            for expense in expenses[:10]:  # Limiter à 10 dépenses
                expenses_data.append([
                    expense.expense_date.strftime('%d/%m'),
                    expense.description[:30] + '...' if len(expense.description) > 30 else expense.description,
                    expense.category,
                    f"{expense.amount:,.0f}"
                ])
            
            expenses_table = Table(expenses_data, colWidths=[1*inch, 2.5*inch, 1.5*inch, 1*inch])
            expenses_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFE6E6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(expenses_table)
            
            if len(expenses) > 10:
                story.append(Paragraph(f"... et {len(expenses) - 10} autres dépenses", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 50))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph("Généré par Akompta AI - CosmoLAB Hub", footer_style))
        story.append(Paragraph(f"Développé par Marino ATOHOUN", footer_style))
        
        # Construire le PDF
        doc.build(story)
        
        return pdf_path
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

@report_bp.route('/<int:report_id>/download', methods=['GET'])
def download_report(report_id):
    """Télécharge un rapport PDF"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        report = Report.query.filter_by(id=report_id, user_id=user.id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        if not report.file_path or not os.path.exists(report.file_path):
            return jsonify({'error': 'Report file not found'}), 404
        
        return send_file(
            report.file_path,
            as_attachment=True,
            download_name=f"rapport_{report.report_type}_{report.id}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Supprime un rapport"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        report = Report.query.filter_by(id=report_id, user_id=user.id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Supprimer le fichier PDF s'il existe
        if report.file_path and os.path.exists(report.file_path):
            try:
                os.remove(report.file_path)
            except:
                pass  # Ignorer les erreurs de suppression de fichier
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Report deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

