from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    """Modelo para representar usuários do sistema."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    
    # Informações básicas
    username = Column(String(80), nullable=False)
    email = Column(String(120), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Autenticação
    password_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # OAuth
    google_id = Column(String(100), nullable=True)
    microsoft_id = Column(String(100), nullable=True)
    
    # Papéis e permissões
    role = Column(String(50), default='user')  # admin, manager, employee, customer
    permissions = Column(Text, nullable=True)  # JSON string com permissões específicas
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Índices únicos compostos para multi-tenancy
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'username', name='uq_tenant_username'),
        db.UniqueConstraint('tenant_id', 'email', name='uq_tenant_email'),
    )
    
    def set_password(self, password):
        """Define a senha do usuário."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """Verifica se o usuário tem uma permissão específica."""
        if self.role == 'admin':
            return True
        
        if not self.permissions:
            return False
        
        import json
        try:
            perms = json.loads(self.permissions)
            return permission in perms
        except (json.JSONDecodeError, TypeError):
            return False
    
    def get_full_name(self):
        """Retorna o nome completo do usuário."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self, include_sensitive=False):
        """Converte o objeto para dicionário."""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'full_name': self.get_full_name()
        }
        
        if include_sensitive:
            data.update({
                'permissions': self.permissions,
                'google_id': self.google_id,
                'microsoft_id': self.microsoft_id
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.username}@{self.tenant_id}>'
