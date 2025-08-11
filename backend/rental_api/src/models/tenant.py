from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from src.models.user import db

class Tenant(db.Model):
    """Modelo para representar um tenant (cliente) no sistema SaaS."""
    __tablename__ = 'tenants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)
    domain = Column(String(255), unique=True, nullable=True)
    schema_name = Column(String(100), unique=True, nullable=False)
    
    # Configurações do tenant
    timezone = Column(String(50), default='UTC')
    currency = Column(String(3), default='USD')
    language = Column(String(5), default='en')
    
    # Status e configurações
    is_active = Column(Boolean, default=True)
    max_users = Column(Integer, default=10)
    max_items = Column(Integer, default=100)
    
    # Configurações de pagamento
    stripe_account_id = Column(String(255), nullable=True)
    paypal_account_id = Column(String(255), nullable=True)
    mercadopago_account_id = Column(String(255), nullable=True)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configurações de notificação
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    whatsapp_notifications = Column(Boolean, default=False)
    
    # Configurações de branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default='#007bff')
    secondary_color = Column(String(7), default='#6c757d')
    
    def __repr__(self):
        return f'<Tenant {self.name}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'domain': self.domain,
            'schema_name': self.schema_name,
            'timezone': self.timezone,
            'currency': self.currency,
            'language': self.language,
            'is_active': self.is_active,
            'max_users': self.max_users,
            'max_items': self.max_items,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'whatsapp_notifications': self.whatsapp_notifications,
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color
        }
    
    @classmethod
    def create_tenant(cls, name, subdomain, **kwargs):
        """Cria um novo tenant com schema dedicado."""
        schema_name = f"tenant_{subdomain}"
        tenant = cls(
            name=name,
            subdomain=subdomain,
            schema_name=schema_name,
            **kwargs
        )
        return tenant

