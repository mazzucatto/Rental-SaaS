from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from src.models.user import db, User
from src.models.rental import (
    Category, RentalItem, Customer, Reservation, 
    Contract, Payment, CheckInOut, ReservationStatus, PaymentStatus
)

rental_bp = Blueprint('rental', __name__)

def get_current_tenant_id():
    """Retorna o ID do tenant atual."""
    claims = get_jwt()
    return claims.get('tenant_id')

def require_permission(permission):
    """Decorator para verificar permissões."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404
            
            if user.role == 'admin' or user.has_permission(permission):
                return f(*args, **kwargs)
            
            return jsonify({'error': 'Permissão negada'}), 403
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ===== CATEGORIAS =====

@rental_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Lista categorias do tenant."""
    try:
        tenant_id = get_current_tenant_id()
        categories = Category.query.filter_by(tenant_id=tenant_id).all()
        
        return jsonify([category.to_dict() for category in categories]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/categories', methods=['POST'])
@jwt_required()
@require_permission('manage_categories')
def create_category():
    """Cria uma nova categoria."""
    try:
        tenant_id = get_current_tenant_id()
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Nome da categoria é obrigatório'}), 400
        
        category = Category(
            tenant_id=tenant_id,
            name=data['name'],
            description=data.get('description'),
            icon=data.get('icon'),
            color=data.get('color', '#007bff')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoria criada com sucesso',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== ITENS DE LOCAÇÃO =====

@rental_bp.route('/items', methods=['GET'])
@jwt_required()
def get_items():
    """Lista itens de locação do tenant."""
    try:
        tenant_id = get_current_tenant_id()
        
        # Parâmetros de filtro
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        
        query = RentalItem.query.filter_by(tenant_id=tenant_id)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if search:
            query = query.filter(
                RentalItem.name.contains(search) |
                RentalItem.description.contains(search)
            )
        
        items = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'items': [item.to_dict() for item in items.items],
            'pagination': {
                'page': page,
                'pages': items.pages,
                'per_page': per_page,
                'total': items.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/items', methods=['POST'])
@jwt_required()
@require_permission('manage_items')
def create_item():
    """Cria um novo item de locação."""
    try:
        tenant_id = get_current_tenant_id()
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Nome do item é obrigatório'}), 400
        
        item = RentalItem(
            tenant_id=tenant_id,
            category_id=data.get('category_id'),
            name=data['name'],
            description=data.get('description'),
            sku=data.get('sku'),
            barcode=data.get('barcode'),
            hourly_price=Decimal(str(data['hourly_price'])) if data.get('hourly_price') else None,
            daily_price=Decimal(str(data['daily_price'])) if data.get('daily_price') else None,
            weekly_price=Decimal(str(data['weekly_price'])) if data.get('weekly_price') else None,
            monthly_price=Decimal(str(data['monthly_price'])) if data.get('monthly_price') else None,
            total_quantity=data.get('total_quantity', 1),
            available_quantity=data.get('available_quantity', 1),
            min_rental_hours=data.get('min_rental_hours', 1),
            max_rental_days=data.get('max_rental_days'),
            requires_deposit=data.get('requires_deposit', False),
            deposit_amount=Decimal(str(data['deposit_amount'])) if data.get('deposit_amount') else None,
            attributes=data.get('attributes'),
            specifications=data.get('specifications'),
            images=data.get('images'),
            documents=data.get('documents')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'message': 'Item criado com sucesso',
            'item': item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/items/<int:item_id>', methods=['GET'])
@jwt_required()
def get_item(item_id):
    """Retorna detalhes de um item específico."""
    try:
        tenant_id = get_current_tenant_id()
        item = RentalItem.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        return jsonify(item.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
@require_permission('manage_items')
def update_item(item_id):
    """Atualiza um item de locação."""
    try:
        tenant_id = get_current_tenant_id()
        item = RentalItem.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        updatable_fields = [
            'category_id', 'name', 'description', 'sku', 'barcode',
            'total_quantity', 'available_quantity', 'min_rental_hours',
            'max_rental_days', 'status', 'is_active', 'requires_deposit',
            'attributes', 'specifications', 'images', 'documents'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(item, field, data[field])
        
        # Campos de preço (converter para Decimal)
        price_fields = ['hourly_price', 'daily_price', 'weekly_price', 'monthly_price', 'deposit_amount']
        for field in price_fields:
            if field in data and data[field] is not None:
                setattr(item, field, Decimal(str(data[field])))
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Item atualizado com sucesso',
            'item': item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== CLIENTES =====

@rental_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    """Lista clientes do tenant."""
    try:
        tenant_id = get_current_tenant_id()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search')
        
        query = Customer.query.filter_by(tenant_id=tenant_id)
        
        if search:
            query = query.filter(
                Customer.first_name.contains(search) |
                Customer.last_name.contains(search) |
                Customer.email.contains(search)
            )
        
        customers = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'customers': [customer.to_dict() for customer in customers.items],
            'pagination': {
                'page': page,
                'pages': customers.pages,
                'per_page': per_page,
                'total': customers.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/customers', methods=['POST'])
@jwt_required()
@require_permission('manage_customers')
def create_customer():
    """Cria um novo cliente."""
    try:
        tenant_id = get_current_tenant_id()
        data = request.get_json()
        
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        customer = Customer(
            tenant_id=tenant_id,
            user_id=data.get('user_id'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            document_type=data.get('document_type'),
            document_number=data.get('document_number'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            country=data.get('country'),
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_phone=data.get('emergency_contact_phone'),
            credit_limit=Decimal(str(data['credit_limit'])) if data.get('credit_limit') else None
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'message': 'Cliente criado com sucesso',
            'customer': customer.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== RESERVAS =====

@rental_bp.route('/reservations', methods=['GET'])
@jwt_required()
def get_reservations():
    """Lista reservas do tenant."""
    try:
        tenant_id = get_current_tenant_id()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        item_id = request.args.get('item_id', type=int)
        customer_id = request.args.get('customer_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Reservation.query.filter_by(tenant_id=tenant_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if item_id:
            query = query.filter_by(item_id=item_id)
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Reservation.start_date >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Reservation.end_date <= end_dt)
        
        reservations = query.order_by(Reservation.start_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'reservations': [reservation.to_dict() for reservation in reservations.items],
            'pagination': {
                'page': page,
                'pages': reservations.pages,
                'per_page': per_page,
                'total': reservations.total
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/reservations', methods=['POST'])
@jwt_required()
@require_permission('manage_reservations')
def create_reservation():
    """Cria uma nova reserva."""
    try:
        tenant_id = get_current_tenant_id()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['item_id', 'customer_id', 'start_date', 'end_date', 'quantity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se o item existe e está disponível
        item = RentalItem.query.filter_by(id=data['item_id'], tenant_id=tenant_id).first()
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        if not item.is_active:
            return jsonify({'error': 'Item não está ativo'}), 400
        
        # Verificar disponibilidade
        quantity = data['quantity']
        if quantity > item.available_quantity:
            return jsonify({'error': 'Quantidade não disponível'}), 400
        
        # Verificar se o cliente existe
        customer = Customer.query.filter_by(id=data['customer_id'], tenant_id=tenant_id).first()
        if not customer:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        # Calcular preços
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
        
        # Lógica simples de cálculo de preço (pode ser melhorada)
        duration = end_date - start_date
        hours = duration.total_seconds() / 3600
        
        if hours <= 24 and item.hourly_price:
            unit_price = item.hourly_price * Decimal(str(hours))
        elif hours <= 168 and item.daily_price:  # 7 dias
            days = max(1, int(hours / 24))
            unit_price = item.daily_price * Decimal(str(days))
        elif hours <= 720 and item.weekly_price:  # 30 dias
            weeks = max(1, int(hours / 168))
            unit_price = item.weekly_price * Decimal(str(weeks))
        elif item.monthly_price:
            months = max(1, int(hours / 720))
            unit_price = item.monthly_price * Decimal(str(months))
        else:
            return jsonify({'error': 'Não foi possível calcular o preço'}), 400
        
        total_price = unit_price * Decimal(str(quantity))
        deposit_amount = item.deposit_amount * Decimal(str(quantity)) if item.requires_deposit else Decimal('0')
        additional_fees = Decimal(str(data.get('additional_fees', 0)))
        discount_amount = Decimal(str(data.get('discount_amount', 0)))
        final_amount = total_price + deposit_amount + additional_fees - discount_amount
        
        # Gerar código único da reserva
        reservation_code = f"RES-{uuid.uuid4().hex[:8].upper()}"
        
        reservation = Reservation(
            tenant_id=tenant_id,
            item_id=data['item_id'],
            customer_id=data['customer_id'],
            reservation_code=reservation_code,
            start_date=start_date,
            end_date=end_date,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            deposit_amount=deposit_amount,
            additional_fees=additional_fees,
            discount_amount=discount_amount,
            final_amount=final_amount,
            notes=data.get('notes'),
            internal_notes=data.get('internal_notes'),
            created_by=current_user_id
        )
        
        # Atualizar disponibilidade do item
        item.available_quantity -= quantity
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'message': 'Reserva criada com sucesso',
            'reservation': reservation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rental_bp.route('/reservations/<int:reservation_id>/confirm', methods=['POST'])
@jwt_required()
@require_permission('manage_reservations')
def confirm_reservation(reservation_id):
    """Confirma uma reserva."""
    try:
        tenant_id = get_current_tenant_id()
        reservation = Reservation.query.filter_by(
            id=reservation_id, 
            tenant_id=tenant_id
        ).first()
        
        if not reservation:
            return jsonify({'error': 'Reserva não encontrada'}), 404
        
        if reservation.status != ReservationStatus.PENDING.value:
            return jsonify({'error': 'Reserva não pode ser confirmada'}), 400
        
        reservation.status = ReservationStatus.CONFIRMED.value
        reservation.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reserva confirmada com sucesso',
            'reservation': reservation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== AGENDA =====

@rental_bp.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar():
    """Retorna eventos do calendário de reservas."""
    try:
        tenant_id = get_current_tenant_id()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'start_date e end_date são obrigatórios'}), 400
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        reservations = Reservation.query.filter_by(tenant_id=tenant_id).filter(
            Reservation.start_date <= end_dt,
            Reservation.end_date >= start_dt
        ).all()
        
        events = []
        for reservation in reservations:
            events.append({
                'id': reservation.id,
                'title': f"{reservation.item.name} - {reservation.customer.get_full_name()}",
                'start': reservation.start_date.isoformat(),
                'end': reservation.end_date.isoformat(),
                'status': reservation.status,
                'item_id': reservation.item_id,
                'customer_id': reservation.customer_id,
                'reservation_code': reservation.reservation_code
            })
        
        return jsonify({'events': events}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== DASHBOARD =====

@rental_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Retorna dados para o dashboard."""
    try:
        tenant_id = get_current_tenant_id()
        
        # Estatísticas gerais
        total_items = RentalItem.query.filter_by(tenant_id=tenant_id).count()
        active_items = RentalItem.query.filter_by(tenant_id=tenant_id, is_active=True).count()
        total_customers = Customer.query.filter_by(tenant_id=tenant_id).count()
        
        # Reservas por status
        reservations_stats = {}
        for status in ReservationStatus:
            count = Reservation.query.filter_by(
                tenant_id=tenant_id, 
                status=status.value
            ).count()
            reservations_stats[status.value] = count
        
        # Reservas recentes
        recent_reservations = Reservation.query.filter_by(tenant_id=tenant_id).order_by(
            Reservation.created_at.desc()
        ).limit(5).all()
        
        # Próximas reservas
        upcoming_reservations = Reservation.query.filter_by(tenant_id=tenant_id).filter(
            Reservation.start_date > datetime.utcnow(),
            Reservation.status.in_(['confirmed', 'pending'])
        ).order_by(Reservation.start_date).limit(5).all()
        
        dashboard_data = {
            'stats': {
                'total_items': total_items,
                'active_items': active_items,
                'total_customers': total_customers,
                'reservations': reservations_stats
            },
            'recent_reservations': [r.to_dict() for r in recent_reservations],
            'upcoming_reservations': [r.to_dict() for r in upcoming_reservations]
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

