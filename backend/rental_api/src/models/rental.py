from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import relationship
from enum import Enum
from src.models.user import db

class ItemStatus(Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"

class ReservationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    PIX = "pix"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_SLIP = "bank_slip"
    CASH = "cash"

class Category(db.Model):
    """Modelo para categorias de itens de locação."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), default='#007bff')
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    items = relationship("RentalItem", back_populates="category")
    
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uq_tenant_category_name'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RentalItem(db.Model):
    """Modelo para itens disponíveis para locação."""
    __tablename__ = 'rental_items'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # Informações básicas
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String(100), nullable=True)
    barcode = Column(String(100), nullable=True)
    
    # Preços
    hourly_price = Column(Numeric(10, 2), nullable=True)
    daily_price = Column(Numeric(10, 2), nullable=True)
    weekly_price = Column(Numeric(10, 2), nullable=True)
    monthly_price = Column(Numeric(10, 2), nullable=True)
    
    # Estoque e disponibilidade
    total_quantity = Column(Integer, default=1)
    available_quantity = Column(Integer, default=1)
    min_rental_hours = Column(Integer, default=1)
    max_rental_days = Column(Integer, nullable=True)
    
    # Status e configurações
    status = Column(String(20), default=ItemStatus.AVAILABLE.value)
    is_active = Column(Boolean, default=True)
    requires_deposit = Column(Boolean, default=False)
    deposit_amount = Column(Numeric(10, 2), nullable=True)
    
    # Atributos e especificações
    attributes = Column(JSON, nullable=True)  # {"color": "red", "size": "large", etc.}
    specifications = Column(Text, nullable=True)
    
    # Imagens e documentos
    images = Column(JSON, nullable=True)  # Lista de URLs das imagens
    documents = Column(JSON, nullable=True)  # Manuais, certificados, etc.
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    category = relationship("Category", back_populates="items")
    reservations = relationship("Reservation", back_populates="item")
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'sku': self.sku,
            'barcode': self.barcode,
            'hourly_price': float(self.hourly_price) if self.hourly_price else None,
            'daily_price': float(self.daily_price) if self.daily_price else None,
            'weekly_price': float(self.weekly_price) if self.weekly_price else None,
            'monthly_price': float(self.monthly_price) if self.monthly_price else None,
            'total_quantity': self.total_quantity,
            'available_quantity': self.available_quantity,
            'min_rental_hours': self.min_rental_hours,
            'max_rental_days': self.max_rental_days,
            'status': self.status,
            'is_active': self.is_active,
            'requires_deposit': self.requires_deposit,
            'deposit_amount': float(self.deposit_amount) if self.deposit_amount else None,
            'attributes': self.attributes,
            'specifications': self.specifications,
            'images': self.images,
            'documents': self.documents,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category': self.category.to_dict() if self.category else None
        }

class Customer(db.Model):
    """Modelo para clientes que fazem locações."""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Se for usuário registrado
    
    # Informações pessoais
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Documentos
    document_type = Column(String(20), nullable=True)  # CPF, CNPJ, Passport, etc.
    document_number = Column(String(50), nullable=True)
    
    # Endereço
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    
    # Informações de contato de emergência
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    credit_limit = Column(Numeric(10, 2), nullable=True)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    reservations = relationship("Reservation", back_populates="customer")
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'email': self.email,
            'phone': self.phone,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'is_active': self.is_active,
            'credit_limit': float(self.credit_limit) if self.credit_limit else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Reservation(db.Model):
    """Modelo para reservas de locação."""
    __tablename__ = 'reservations'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('rental_items.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Código de reserva único
    reservation_code = Column(String(20), unique=True, nullable=False)
    
    # Datas e horários
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    
    # Quantidades
    quantity = Column(Integer, default=1)
    
    # Valores
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), nullable=True)
    additional_fees = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    final_amount = Column(Numeric(10, 2), nullable=False)
    
    # Status e configurações
    status = Column(String(20), default=ReservationStatus.PENDING.value)
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(JSON, nullable=True)  # Padrão de recorrência
    
    # Observações
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relacionamentos
    item = relationship("RentalItem", back_populates="reservations")
    customer = relationship("Customer", back_populates="reservations")
    contract = relationship("Contract", back_populates="reservation", uselist=False)
    payments = relationship("Payment", back_populates="reservation")
    checkins = relationship("CheckInOut", back_populates="reservation")
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'item_id': self.item_id,
            'customer_id': self.customer_id,
            'reservation_code': self.reservation_code,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_price': float(self.total_price) if self.total_price else None,
            'deposit_amount': float(self.deposit_amount) if self.deposit_amount else None,
            'additional_fees': float(self.additional_fees) if self.additional_fees else None,
            'discount_amount': float(self.discount_amount) if self.discount_amount else None,
            'final_amount': float(self.final_amount) if self.final_amount else None,
            'status': self.status,
            'is_recurring': self.is_recurring,
            'recurring_pattern': self.recurring_pattern,
            'notes': self.notes,
            'internal_notes': self.internal_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'item': self.item.to_dict() if self.item else None,
            'customer': self.customer.to_dict() if self.customer else None
        }

class Contract(db.Model):
    """Modelo para contratos de locação."""
    __tablename__ = 'contracts'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    reservation_id = Column(Integer, ForeignKey('reservations.id'), nullable=False)
    
    # Informações do contrato
    contract_number = Column(String(50), unique=True, nullable=False)
    contract_template_id = Column(Integer, nullable=True)
    
    # Conteúdo do contrato
    contract_content = Column(Text, nullable=False)
    terms_and_conditions = Column(Text, nullable=True)
    
    # Assinatura eletrônica
    is_signed = Column(Boolean, default=False)
    signed_at = Column(DateTime, nullable=True)
    signature_data = Column(JSON, nullable=True)  # Dados da assinatura eletrônica
    
    # Status
    status = Column(String(20), default='draft')  # draft, sent, signed, executed, terminated
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    reservation = relationship("Reservation", back_populates="contract")
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'reservation_id': self.reservation_id,
            'contract_number': self.contract_number,
            'contract_template_id': self.contract_template_id,
            'contract_content': self.contract_content,
            'terms_and_conditions': self.terms_and_conditions,
            'is_signed': self.is_signed,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'signature_data': self.signature_data,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Payment(db.Model):
    """Modelo para pagamentos."""
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    reservation_id = Column(Integer, ForeignKey('reservations.id'), nullable=False)
    
    # Informações do pagamento
    payment_code = Column(String(50), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD')
    
    # Método e gateway
    payment_method = Column(String(20), nullable=False)
    gateway = Column(String(50), nullable=True)  # stripe, paypal, mercadopago
    gateway_transaction_id = Column(String(200), nullable=True)
    
    # Status e datas
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    paid_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    # Dados adicionais
    payment_data = Column(JSON, nullable=True)  # Dados específicos do gateway
    failure_reason = Column(Text, nullable=True)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    reservation = relationship("Reservation", back_populates="payments")
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'reservation_id': self.reservation_id,
            'payment_code': self.payment_code,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'gateway': self.gateway,
            'gateway_transaction_id': self.gateway_transaction_id,
            'status': self.status,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'payment_data': self.payment_data,
            'failure_reason': self.failure_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CheckInOut(db.Model):
    """Modelo para check-in e check-out."""
    __tablename__ = 'checkin_checkout'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    reservation_id = Column(Integer, ForeignKey('reservations.id'), nullable=False)
    
    # Tipo de operação
    operation_type = Column(String(10), nullable=False)  # checkin, checkout
    
    # Data e responsável
    operation_date = Column(DateTime, default=datetime.utcnow)
    performed_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Condições do item
    item_condition = Column(String(20), nullable=False)  # excellent, good, fair, poor, damaged
    condition_notes = Column(Text, nullable=True)
    
    # Fotos e documentos
    photos = Column(JSON, nullable=True)  # Lista de URLs das fotos
    documents = Column(JSON, nullable=True)
    
    # Observações
    notes = Column(Text, nullable=True)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    reservation = relationship("Reservation", back_populates="checkins")
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'reservation_id': self.reservation_id,
            'operation_type': self.operation_type,
            'operation_date': self.operation_date.isoformat() if self.operation_date else None,
            'performed_by': self.performed_by,
            'item_condition': self.item_condition,
            'condition_notes': self.condition_notes,
            'photos': self.photos,
            'documents': self.documents,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

