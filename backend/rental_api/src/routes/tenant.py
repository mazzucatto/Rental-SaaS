from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

from src.models.user import db, User
from src.models.tenant import Tenant

tenant_bp = Blueprint('tenant', __name__)

def require_admin():
    """Decorator para verificar se o usuário é admin."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != 'admin':
                return jsonify({'error': 'Acesso negado. Apenas administradores.'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@tenant_bp.route('/', methods=['GET'])
@jwt_required()
@require_admin()
def get_tenant():
    """Retorna informações do tenant atual."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant não encontrado'}), 404
        
        return jsonify(tenant.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/', methods=['PUT'])
@jwt_required()
@require_admin()
def update_tenant():
    """Atualiza informações do tenant."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant não encontrado'}), 404
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        updatable_fields = [
            'name', 'domain', 'timezone', 'currency', 'language',
            'max_users', 'max_items', 'email_notifications',
            'sms_notifications', 'whatsapp_notifications',
            'logo_url', 'primary_color', 'secondary_color'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(tenant, field, data[field])
        
        tenant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Tenant atualizado com sucesso',
            'tenant': tenant.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/settings', methods=['GET'])
@jwt_required()
@require_admin()
def get_tenant_settings():
    """Retorna configurações específicas do tenant."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant não encontrado'}), 404
        
        settings = {
            'notifications': {
                'email': tenant.email_notifications,
                'sms': tenant.sms_notifications,
                'whatsapp': tenant.whatsapp_notifications
            },
            'branding': {
                'logo_url': tenant.logo_url,
                'primary_color': tenant.primary_color,
                'secondary_color': tenant.secondary_color
            },
            'limits': {
                'max_users': tenant.max_users,
                'max_items': tenant.max_items
            },
            'localization': {
                'timezone': tenant.timezone,
                'currency': tenant.currency,
                'language': tenant.language
            },
            'payments': {
                'stripe_configured': bool(tenant.stripe_account_id),
                'paypal_configured': bool(tenant.paypal_account_id),
                'mercadopago_configured': bool(tenant.mercadopago_account_id)
            }
        }
        
        return jsonify(settings), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/settings', methods=['PUT'])
@jwt_required()
@require_admin()
def update_tenant_settings():
    """Atualiza configurações específicas do tenant."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar notificações
        if 'notifications' in data:
            notifications = data['notifications']
            if 'email' in notifications:
                tenant.email_notifications = notifications['email']
            if 'sms' in notifications:
                tenant.sms_notifications = notifications['sms']
            if 'whatsapp' in notifications:
                tenant.whatsapp_notifications = notifications['whatsapp']
        
        # Atualizar branding
        if 'branding' in data:
            branding = data['branding']
            if 'logo_url' in branding:
                tenant.logo_url = branding['logo_url']
            if 'primary_color' in branding:
                tenant.primary_color = branding['primary_color']
            if 'secondary_color' in branding:
                tenant.secondary_color = branding['secondary_color']
        
        # Atualizar limites
        if 'limits' in data:
            limits = data['limits']
            if 'max_users' in limits:
                tenant.max_users = limits['max_users']
            if 'max_items' in limits:
                tenant.max_items = limits['max_items']
        
        # Atualizar localização
        if 'localization' in data:
            localization = data['localization']
            if 'timezone' in localization:
                tenant.timezone = localization['timezone']
            if 'currency' in localization:
                tenant.currency = localization['currency']
            if 'language' in localization:
                tenant.language = localization['language']
        
        # Atualizar configurações de pagamento
        if 'payments' in data:
            payments = data['payments']
            if 'stripe_account_id' in payments:
                tenant.stripe_account_id = payments['stripe_account_id']
            if 'paypal_account_id' in payments:
                tenant.paypal_account_id = payments['paypal_account_id']
            if 'mercadopago_account_id' in payments:
                tenant.mercadopago_account_id = payments['mercadopago_account_id']
        
        tenant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Configurações atualizadas com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_admin()
def get_tenant_stats():
    """Retorna estatísticas do tenant."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        # Importar modelos aqui para evitar importação circular
        from src.models.rental import RentalItem, Reservation, Customer
        
        # Contar usuários
        users_count = User.query.filter_by(tenant_id=tenant_id).count()
        
        # Contar itens
        items_count = RentalItem.query.filter_by(tenant_id=tenant_id).count()
        active_items_count = RentalItem.query.filter_by(
            tenant_id=tenant_id, 
            is_active=True
        ).count()
        
        # Contar reservas
        reservations_count = Reservation.query.filter_by(tenant_id=tenant_id).count()
        active_reservations_count = Reservation.query.filter_by(
            tenant_id=tenant_id
        ).filter(
            Reservation.status.in_(['confirmed', 'active'])
        ).count()
        
        # Contar clientes
        customers_count = Customer.query.filter_by(tenant_id=tenant_id).count()
        
        stats = {
            'users': {
                'total': users_count,
                'limit': Tenant.query.get(tenant_id).max_users
            },
            'items': {
                'total': items_count,
                'active': active_items_count,
                'limit': Tenant.query.get(tenant_id).max_items
            },
            'reservations': {
                'total': reservations_count,
                'active': active_reservations_count
            },
            'customers': {
                'total': customers_count
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/users', methods=['GET'])
@jwt_required()
@require_admin()
def get_tenant_users():
    """Lista usuários do tenant."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.filter_by(tenant_id=tenant_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'pages': users.pages,
                'per_page': per_page,
                'total': users.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/users', methods=['POST'])
@jwt_required()
@require_admin()
def create_tenant_user():
    """Cria um novo usuário no tenant."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se o email já existe para este tenant
        existing_user = User.query.filter_by(
            tenant_id=tenant_id, 
            email=data['email']
        ).first()
        if existing_user:
            return jsonify({'error': 'Email já está em uso neste tenant'}), 400
        
        # Verificar limite de usuários
        tenant = Tenant.query.get(tenant_id)
        current_users = User.query.filter_by(tenant_id=tenant_id).count()
        if current_users >= tenant.max_users:
            return jsonify({'error': 'Limite de usuários atingido'}), 400
        
        # Criar usuário
        user = User(
            tenant_id=tenant_id,
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

