# Security Guide - Rental SaaS

This document outlines the security measures, best practices, and guidelines implemented in the Rental SaaS system.

## Table of Contents

- [Security Overview](#security-overview)
- [Authentication & Authorization](#authentication--authorization)
- [Data Protection](#data-protection)
- [Network Security](#network-security)
- [Application Security](#application-security)
- [Infrastructure Security](#infrastructure-security)
- [Compliance & Standards](#compliance--standards)
- [Security Monitoring](#security-monitoring)
- [Incident Response](#incident-response)
- [Security Best Practices](#security-best-practices)

## Security Overview

Rental SaaS implements a comprehensive security framework designed to protect sensitive data, ensure system integrity, and maintain user privacy. Our security approach follows industry best practices and compliance standards.

### Security Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimal access rights for users and systems
3. **Zero Trust**: Never trust, always verify
4. **Data Minimization**: Collect and store only necessary data
5. **Transparency**: Clear security policies and procedures

### Threat Model

We protect against the following threat categories:

- **External Attackers**: Unauthorized access attempts
- **Insider Threats**: Malicious or negligent internal users
- **Data Breaches**: Unauthorized data access or exfiltration
- **Service Disruption**: DDoS attacks and system availability threats
- **Supply Chain Attacks**: Compromised dependencies or third-party services

## Authentication & Authorization

### Multi-Factor Authentication (MFA)

```python
# src/utils/mfa.py
import pyotp
import qrcode
from io import BytesIO
import base64

class MFAService:
    @staticmethod
    def generate_secret():
        """Generate a new TOTP secret for user."""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(user_email, secret, issuer="Rental SaaS"):
        """Generate QR code for TOTP setup."""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_token(secret, token):
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
```

### JWT Token Security

```python
# src/utils/jwt_security.py
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
import secrets

class JWTSecurity:
    # Token expiration times
    ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    @staticmethod
    def create_tokens(user_identity):
        """Create access and refresh tokens with security claims."""
        additional_claims = {
            "tenant_id": user_identity.get("tenant_id"),
            "permissions": user_identity.get("permissions", []),
            "session_id": secrets.token_urlsafe(32),
            "ip_address": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", "")[:200]
        }
        
        access_token = create_access_token(
            identity=user_identity,
            expires_delta=cls.ACCESS_TOKEN_EXPIRES,
            additional_claims=additional_claims
        )
        
        refresh_token = create_refresh_token(
            identity=user_identity,
            expires_delta=cls.REFRESH_TOKEN_EXPIRES
        )
        
        return access_token, refresh_token
    
    @staticmethod
    def validate_token_context(claims):
        """Validate token context for security."""
        # Check IP address consistency
        if claims.get("ip_address") != request.remote_addr:
            raise SecurityException("IP address mismatch")
        
        # Check user agent consistency
        current_ua = request.headers.get("User-Agent", "")[:200]
        if claims.get("user_agent") != current_ua:
            raise SecurityException("User agent mismatch")
```

### Role-Based Access Control (RBAC)

```python
# src/models/permissions.py
class Permission:
    # Item management
    MANAGE_ITEMS = "manage_items"
    VIEW_ITEMS = "view_items"
    
    # Customer management
    MANAGE_CUSTOMERS = "manage_customers"
    VIEW_CUSTOMERS = "view_customers"
    
    # Reservation management
    MANAGE_RESERVATIONS = "manage_reservations"
    VIEW_RESERVATIONS = "view_reservations"
    
    # Financial operations
    MANAGE_PAYMENTS = "manage_payments"
    VIEW_FINANCIAL_REPORTS = "view_financial_reports"
    
    # System administration
    MANAGE_USERS = "manage_users"
    MANAGE_TENANT_SETTINGS = "manage_tenant_settings"
    VIEW_SYSTEM_LOGS = "view_system_logs"

class Role:
    ADMIN = {
        Permission.MANAGE_ITEMS,
        Permission.MANAGE_CUSTOMERS,
        Permission.MANAGE_RESERVATIONS,
        Permission.MANAGE_PAYMENTS,
        Permission.VIEW_FINANCIAL_REPORTS,
        Permission.MANAGE_USERS,
        Permission.MANAGE_TENANT_SETTINGS,
        Permission.VIEW_SYSTEM_LOGS
    }
    
    MANAGER = {
        Permission.MANAGE_ITEMS,
        Permission.MANAGE_CUSTOMERS,
        Permission.MANAGE_RESERVATIONS,
        Permission.VIEW_FINANCIAL_REPORTS
    }
    
    EMPLOYEE = {
        Permission.VIEW_ITEMS,
        Permission.VIEW_CUSTOMERS,
        Permission.MANAGE_RESERVATIONS
    }
    
    CUSTOMER = {
        Permission.VIEW_ITEMS
    }
```

### Session Management

```python
# src/utils/session_security.py
import redis
import json
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_timeout = timedelta(hours=24)
    
    def create_session(self, user_id, session_data):
        """Create a new user session."""
        session_id = secrets.token_urlsafe(32)
        session_key = f"session:{session_id}"
        
        session_info = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "ip_address": session_data.get("ip_address"),
            "user_agent": session_data.get("user_agent"),
            "is_active": True
        }
        
        self.redis.setex(
            session_key,
            self.session_timeout,
            json.dumps(session_info)
        )
        
        return session_id
    
    def validate_session(self, session_id, current_ip, current_ua):
        """Validate session and update activity."""
        session_key = f"session:{session_id}"
        session_data = self.redis.get(session_key)
        
        if not session_data:
            raise SecurityException("Invalid session")
        
        session_info = json.loads(session_data)
        
        # Check if session is active
        if not session_info.get("is_active"):
            raise SecurityException("Session deactivated")
        
        # Update last activity
        session_info["last_activity"] = datetime.utcnow().isoformat()
        self.redis.setex(session_key, self.session_timeout, json.dumps(session_info))
        
        return session_info
    
    def revoke_session(self, session_id):
        """Revoke a specific session."""
        session_key = f"session:{session_id}"
        self.redis.delete(session_key)
    
    def revoke_all_user_sessions(self, user_id):
        """Revoke all sessions for a user."""
        pattern = f"session:*"
        for key in self.redis.scan_iter(match=pattern):
            session_data = self.redis.get(key)
            if session_data:
                session_info = json.loads(session_data)
                if session_info.get("user_id") == user_id:
                    self.redis.delete(key)
```

## Data Protection

### Encryption at Rest

```python
# src/utils/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataEncryption:
    def __init__(self, password=None):
        if password is None:
            password = os.environ.get('ENCRYPTION_KEY', '').encode()
        
        salt = os.environ.get('ENCRYPTION_SALT', 'default_salt').encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        """Encrypt sensitive data."""
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt sensitive data."""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.cipher.decrypt(encrypted_data).decode()

# Usage in models
class Customer(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    _document_number = db.Column(db.Text)  # Encrypted field
    
    @property
    def document_number(self):
        if self._document_number:
            return DataEncryption().decrypt(self._document_number)
        return None
    
    @document_number.setter
    def document_number(self, value):
        if value:
            self._document_number = DataEncryption().encrypt(value)
        else:
            self._document_number = None
```

### Data Anonymization

```python
# src/utils/anonymization.py
import hashlib
import random
import string

class DataAnonymizer:
    @staticmethod
    def anonymize_email(email):
        """Anonymize email address."""
        local, domain = email.split('@')
        anonymized_local = hashlib.sha256(local.encode()).hexdigest()[:8]
        return f"{anonymized_local}@{domain}"
    
    @staticmethod
    def anonymize_phone(phone):
        """Anonymize phone number."""
        return f"***-***-{phone[-4:]}" if len(phone) >= 4 else "***-***-****"
    
    @staticmethod
    def anonymize_name(name):
        """Anonymize personal name."""
        parts = name.split()
        if len(parts) > 1:
            return f"{parts[0][0]}*** {parts[-1][0]}***"
        return f"{name[0]}***"
    
    @staticmethod
    def generate_fake_data(data_type):
        """Generate fake data for testing."""
        if data_type == "email":
            return f"test{''.join(random.choices(string.digits, k=6))}@example.com"
        elif data_type == "phone":
            return f"+1555{''.join(random.choices(string.digits, k=7))}"
        elif data_type == "name":
            first_names = ["John", "Jane", "Bob", "Alice", "Charlie"]
            last_names = ["Doe", "Smith", "Johnson", "Brown", "Davis"]
            return f"{random.choice(first_names)} {random.choice(last_names)}"
```

### Data Retention and Deletion

```python
# src/utils/data_retention.py
from datetime import datetime, timedelta
from sqlalchemy import and_

class DataRetentionService:
    # Retention periods (in days)
    CUSTOMER_DATA_RETENTION = 2555  # 7 years
    RESERVATION_DATA_RETENTION = 2555  # 7 years
    LOG_DATA_RETENTION = 365  # 1 year
    SESSION_DATA_RETENTION = 30  # 30 days
    
    @classmethod
    def cleanup_expired_data(cls):
        """Remove expired data according to retention policies."""
        cutoff_date = datetime.utcnow() - timedelta(days=cls.LOG_DATA_RETENTION)
        
        # Clean up old logs
        AuditLog.query.filter(AuditLog.created_at < cutoff_date).delete()
        
        # Clean up old sessions
        session_cutoff = datetime.utcnow() - timedelta(days=cls.SESSION_DATA_RETENTION)
        # Redis sessions will expire automatically
        
        # Anonymize old customer data (instead of deletion for legal compliance)
        anonymization_cutoff = datetime.utcnow() - timedelta(days=cls.CUSTOMER_DATA_RETENTION)
        old_customers = Customer.query.filter(
            and_(
                Customer.created_at < anonymization_cutoff,
                Customer.is_anonymized == False
            )
        ).all()
        
        for customer in old_customers:
            cls.anonymize_customer(customer)
        
        db.session.commit()
    
    @staticmethod
    def anonymize_customer(customer):
        """Anonymize customer data while preserving business records."""
        anonymizer = DataAnonymizer()
        
        customer.full_name = anonymizer.anonymize_name(customer.full_name)
        customer.email = anonymizer.anonymize_email(customer.email)
        customer.phone = anonymizer.anonymize_phone(customer.phone)
        customer.address = "*** ANONYMIZED ***"
        customer.document_number = None
        customer.is_anonymized = True
        customer.anonymized_at = datetime.utcnow()
```

## Network Security

### HTTPS/TLS Configuration

```nginx
# nginx/conf.d/ssl.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL Certificate
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';" always;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/ssl/certs/ca-certificates.crt;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Rate Limiting

```python
# src/utils/rate_limiting.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

class RateLimiter:
    def __init__(self, app, redis_client):
        self.limiter = Limiter(
            app,
            key_func=get_remote_address,
            storage_uri=f"redis://{redis_client.connection_pool.connection_kwargs['host']}:{redis_client.connection_pool.connection_kwargs['port']}/1"
        )
        
        # Configure rate limits
        self.setup_rate_limits()
    
    def setup_rate_limits(self):
        """Configure rate limits for different endpoints."""
        
        # Authentication endpoints - stricter limits
        @self.limiter.limit("5 per minute")
        def auth_rate_limit():
            pass
        
        # API endpoints - general limits
        @self.limiter.limit("100 per minute")
        def api_rate_limit():
            pass
        
        # File upload endpoints - very strict
        @self.limiter.limit("10 per minute")
        def upload_rate_limit():
            pass

# Usage in routes
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login implementation
    pass

@rental_bp.route('/items', methods=['GET'])
@limiter.limit("100 per minute")
def get_items():
    # Get items implementation
    pass
```

### CORS Configuration

```python
# src/utils/cors_config.py
from flask_cors import CORS

def configure_cors(app):
    """Configure CORS with security considerations."""
    
    # Production CORS configuration
    if app.config.get('ENV') == 'production':
        CORS(app, 
             origins=app.config.get('CORS_ORIGINS', []),
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
             allow_headers=['Content-Type', 'Authorization'],
             supports_credentials=True,
             max_age=86400  # 24 hours
        )
    else:
        # Development CORS configuration
        CORS(app, 
             origins=['http://localhost:3000', 'http://localhost:5173'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
             allow_headers=['Content-Type', 'Authorization'],
             supports_credentials=True
        )
```

## Application Security

### Input Validation and Sanitization

```python
# src/utils/validation.py
from marshmallow import Schema, fields, validate, ValidationError
import bleach
import re

class SecurityValidator:
    @staticmethod
    def sanitize_html(text):
        """Remove potentially dangerous HTML."""
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
        return bleach.clean(text, tags=allowed_tags, strip=True)
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")
        return email.lower()
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format."""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValidationError("Invalid phone number")
        return digits_only
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength."""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain lowercase letter")
        
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain special character")
        
        return password

# Schema examples
class ItemSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(validate=validate.Length(max=1000))
    sku = fields.Str(required=True, validate=validate.Regexp(r'^[A-Z0-9-]+$'))
    daily_price = fields.Decimal(required=True, validate=validate.Range(min=0))
    
    def load(self, json_data, *args, **kwargs):
        # Sanitize description
        if 'description' in json_data:
            json_data['description'] = SecurityValidator.sanitize_html(json_data['description'])
        
        return super().load(json_data, *args, **kwargs)
```

### SQL Injection Prevention

```python
# src/utils/database_security.py
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy

class SecureQuery:
    @staticmethod
    def safe_query(query_string, parameters=None):
        """Execute parameterized queries to prevent SQL injection."""
        if parameters is None:
            parameters = {}
        
        # Use SQLAlchemy's text() with bound parameters
        return db.session.execute(text(query_string), parameters)
    
    @staticmethod
    def validate_table_name(table_name):
        """Validate table names for dynamic queries."""
        allowed_tables = [
            'rental_items', 'customers', 'reservations', 
            'payments', 'categories', 'users'
        ]
        
        if table_name not in allowed_tables:
            raise SecurityException(f"Invalid table name: {table_name}")
        
        return table_name

# Example of safe dynamic query
def get_items_by_category(tenant_id, category_name, sort_by='name'):
    # Validate sort column
    allowed_sort_columns = ['name', 'created_at', 'daily_price']
    if sort_by not in allowed_sort_columns:
        sort_by = 'name'
    
    # Use parameterized query
    query = text(f"""
        SELECT ri.* FROM rental_items ri
        JOIN categories c ON ri.category_id = c.id
        WHERE ri.tenant_id = :tenant_id 
        AND c.name = :category_name
        ORDER BY ri.{sort_by}
    """)
    
    return db.session.execute(query, {
        'tenant_id': tenant_id,
        'category_name': category_name
    }).fetchall()
```

### File Upload Security

```python
# src/utils/file_security.py
import os
import magic
from werkzeug.utils import secure_filename
from PIL import Image
import hashlib

class FileUploadSecurity:
    ALLOWED_EXTENSIONS = {
        'image': {'jpg', 'jpeg', 'png', 'gif', 'webp'},
        'document': {'pdf', 'doc', 'docx', 'txt'}
    }
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @classmethod
    def validate_file(cls, file, file_type='image'):
        """Validate uploaded file for security."""
        if not file or not file.filename:
            raise SecurityException("No file provided")
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > cls.MAX_FILE_SIZE:
            raise SecurityException("File too large")
        
        # Check file extension
        filename = secure_filename(file.filename)
        if '.' not in filename:
            raise SecurityException("File must have extension")
        
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in cls.ALLOWED_EXTENSIONS.get(file_type, set()):
            raise SecurityException(f"Invalid file type: {extension}")
        
        # Check MIME type
        file_content = file.read(1024)
        file.seek(0)
        
        mime_type = magic.from_buffer(file_content, mime=True)
        expected_mimes = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'pdf': 'application/pdf'
        }
        
        if mime_type != expected_mimes.get(extension):
            raise SecurityException("File content doesn't match extension")
        
        return filename, extension
    
    @classmethod
    def process_image(cls, file, max_width=1920, max_height=1080):
        """Process and sanitize image files."""
        try:
            image = Image.open(file)
            
            # Remove EXIF data
            if hasattr(image, '_getexif'):
                image = Image.new(image.mode, image.size)
            
            # Resize if too large
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            return image
        except Exception as e:
            raise SecurityException(f"Invalid image file: {str(e)}")
    
    @classmethod
    def generate_safe_filename(cls, original_filename, user_id):
        """Generate a safe, unique filename."""
        extension = original_filename.rsplit('.', 1)[1].lower()
        
        # Create hash of user_id + timestamp + original filename
        hash_input = f"{user_id}_{datetime.utcnow().isoformat()}_{original_filename}"
        file_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        return f"{file_hash}.{extension}"
```

## Infrastructure Security

### Docker Security

```dockerfile
# Secure Dockerfile example
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["python", "src/main.py"]
```

### Environment Security

```bash
# .env.production.example
# Use strong, unique passwords
POSTGRES_PASSWORD=super_secure_random_password_123!@#
REDIS_PASSWORD=another_secure_password_456$%^
SECRET_KEY=very_long_random_secret_key_minimum_32_characters_789&*(
JWT_SECRET_KEY=another_very_long_random_jwt_secret_key_012)!@

# Use secure email configuration
MAIL_SERVER=smtp.secure-provider.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=noreply@yourdomain.com
MAIL_PASSWORD=secure_app_password

# Restrict CORS origins
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Enable security features
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict
```

### Database Security

```sql
-- PostgreSQL security configuration

-- Create application user with limited privileges
CREATE USER rental_app WITH PASSWORD 'secure_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE rental_saas TO rental_app;
GRANT USAGE ON SCHEMA public TO rental_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO rental_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO rental_app;

-- Enable row level security
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE rental_items ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY tenant_isolation ON tenants
    FOR ALL TO rental_app
    USING (id = current_setting('app.current_tenant_id')::uuid);

CREATE POLICY user_tenant_isolation ON users
    FOR ALL TO rental_app
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Enable audit logging
CREATE EXTENSION IF NOT EXISTS pgaudit;
ALTER SYSTEM SET pgaudit.log = 'write, ddl';
SELECT pg_reload_conf();
```

## Compliance & Standards

### GDPR Compliance

```python
# src/utils/gdpr_compliance.py
class GDPRCompliance:
    @staticmethod
    def handle_data_subject_request(request_type, user_email):
        """Handle GDPR data subject requests."""
        user = User.query.filter_by(email=user_email).first()
        if not user:
            raise ValueError("User not found")
        
        if request_type == "access":
            return GDPRCompliance.export_user_data(user)
        elif request_type == "deletion":
            return GDPRCompliance.delete_user_data(user)
        elif request_type == "portability":
            return GDPRCompliance.export_portable_data(user)
        else:
            raise ValueError("Invalid request type")
    
    @staticmethod
    def export_user_data(user):
        """Export all user data for GDPR access request."""
        data = {
            "personal_info": {
                "name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "created_at": user.created_at.isoformat()
            },
            "reservations": [
                {
                    "id": r.id,
                    "item_name": r.item.name,
                    "start_date": r.start_date.isoformat(),
                    "end_date": r.end_date.isoformat(),
                    "amount": float(r.final_amount)
                }
                for r in user.reservations
            ],
            "payments": [
                {
                    "id": p.id,
                    "amount": float(p.amount),
                    "date": p.payment_date.isoformat(),
                    "status": p.status
                }
                for p in user.payments
            ]
        }
        return data
    
    @staticmethod
    def delete_user_data(user):
        """Handle GDPR deletion request."""
        # Check if user has active reservations
        active_reservations = Reservation.query.filter_by(
            customer_id=user.id,
            status__in=['confirmed', 'active']
        ).count()
        
        if active_reservations > 0:
            raise ValueError("Cannot delete user with active reservations")
        
        # Anonymize instead of delete for legal/business records
        anonymizer = DataAnonymizer()
        user.full_name = anonymizer.anonymize_name(user.full_name)
        user.email = anonymizer.anonymize_email(user.email)
        user.phone = anonymizer.anonymize_phone(user.phone)
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        
        db.session.commit()
        
        return {"status": "User data anonymized successfully"}
```

### PCI DSS Compliance

```python
# src/utils/pci_compliance.py
class PCICompliance:
    @staticmethod
    def mask_card_number(card_number):
        """Mask credit card number for display."""
        if len(card_number) < 4:
            return "****"
        return f"****-****-****-{card_number[-4:]}"
    
    @staticmethod
    def validate_card_data_handling():
        """Ensure PCI DSS compliance in card data handling."""
        # Never store full PAN (Primary Account Number)
        # Never store CVV/CVC
        # Never store PIN
        # Encrypt cardholder data if stored
        pass
    
    @staticmethod
    def log_card_data_access(user_id, action, card_last_four):
        """Log access to card data for audit."""
        audit_log = AuditLog(
            user_id=user_id,
            action=f"CARD_DATA_{action}",
            details=f"Accessed card ending in {card_last_four}",
            ip_address=request.remote_addr,
            created_at=datetime.utcnow()
        )
        db.session.add(audit_log)
        db.session.commit()
```

## Security Monitoring

### Audit Logging

```python
# src/utils/audit_logging.py
class AuditLogger:
    @staticmethod
    def log_security_event(event_type, user_id=None, details=None, severity="INFO"):
        """Log security-related events."""
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            details=details or {},
            severity=severity,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            created_at=datetime.utcnow()
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        # Send alert for high-severity events
        if severity in ["WARNING", "ERROR", "CRITICAL"]:
            SecurityAlerts.send_alert(audit_log)
    
    @staticmethod
    def log_data_access(table_name, record_id, action, user_id):
        """Log data access for sensitive tables."""
        AuditLogger.log_security_event(
            event_type="DATA_ACCESS",
            user_id=user_id,
            details={
                "table": table_name,
                "record_id": record_id,
                "action": action
            }
        )

# Decorator for automatic audit logging
def audit_log(action):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity().get('user_id') if get_jwt_identity() else None
            
            try:
                result = f(*args, **kwargs)
                AuditLogger.log_security_event(
                    event_type=action,
                    user_id=user_id,
                    details={"status": "success"}
                )
                return result
            except Exception as e:
                AuditLogger.log_security_event(
                    event_type=action,
                    user_id=user_id,
                    details={"status": "error", "error": str(e)},
                    severity="ERROR"
                )
                raise
        return decorated_function
    return decorator
```

### Intrusion Detection

```python
# src/utils/intrusion_detection.py
class IntrusionDetection:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.thresholds = {
            "failed_logins": 5,
            "api_requests": 1000,
            "file_uploads": 20
        }
    
    def check_failed_logins(self, ip_address):
        """Monitor failed login attempts."""
        key = f"failed_logins:{ip_address}"
        count = self.redis.incr(key)
        self.redis.expire(key, 3600)  # 1 hour window
        
        if count >= self.thresholds["failed_logins"]:
            self.trigger_alert("SUSPICIOUS_LOGIN_ATTEMPTS", {
                "ip_address": ip_address,
                "attempts": count
            })
            return True
        return False
    
    def check_api_abuse(self, user_id):
        """Monitor API request patterns."""
        key = f"api_requests:{user_id}"
        count = self.redis.incr(key)
        self.redis.expire(key, 3600)  # 1 hour window
        
        if count >= self.thresholds["api_requests"]:
            self.trigger_alert("API_ABUSE", {
                "user_id": user_id,
                "requests": count
            })
            return True
        return False
    
    def trigger_alert(self, alert_type, details):
        """Trigger security alert."""
        AuditLogger.log_security_event(
            event_type=alert_type,
            details=details,
            severity="WARNING"
        )
        
        # Block IP or user temporarily
        if alert_type == "SUSPICIOUS_LOGIN_ATTEMPTS":
            self.block_ip(details["ip_address"], duration=3600)
        elif alert_type == "API_ABUSE":
            self.rate_limit_user(details["user_id"], duration=1800)
    
    def block_ip(self, ip_address, duration):
        """Temporarily block IP address."""
        key = f"blocked_ip:{ip_address}"
        self.redis.setex(key, duration, "blocked")
    
    def is_ip_blocked(self, ip_address):
        """Check if IP is blocked."""
        key = f"blocked_ip:{ip_address}"
        return self.redis.exists(key)
```

## Incident Response

### Security Incident Response Plan

```python
# src/utils/incident_response.py
class IncidentResponse:
    SEVERITY_LEVELS = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }
    
    @classmethod
    def handle_security_incident(cls, incident_type, severity, details):
        """Handle security incident according to response plan."""
        incident = SecurityIncident(
            incident_type=incident_type,
            severity=severity,
            details=details,
            status="OPEN",
            created_at=datetime.utcnow()
        )
        
        db.session.add(incident)
        db.session.commit()
        
        # Execute response based on severity
        if severity >= cls.SEVERITY_LEVELS["HIGH"]:
            cls.execute_high_severity_response(incident)
        elif severity >= cls.SEVERITY_LEVELS["MEDIUM"]:
            cls.execute_medium_severity_response(incident)
        else:
            cls.execute_low_severity_response(incident)
    
    @classmethod
    def execute_high_severity_response(cls, incident):
        """Response for high/critical severity incidents."""
        # Immediate actions
        cls.notify_security_team(incident)
        cls.activate_incident_commander(incident)
        
        # Containment actions
        if incident.incident_type == "DATA_BREACH":
            cls.isolate_affected_systems()
            cls.preserve_evidence()
        
        # Communication
        cls.notify_stakeholders(incident)
        
        # Documentation
        cls.start_incident_log(incident)
    
    @classmethod
    def data_breach_response(cls, affected_data, estimated_records):
        """Specific response for data breach incidents."""
        # Immediate containment
        cls.revoke_all_sessions()
        cls.force_password_reset_for_affected_users()
        
        # Legal compliance
        if estimated_records > 500:  # GDPR threshold
            cls.prepare_breach_notification()
        
        # Customer communication
        cls.prepare_customer_notification(affected_data)
        
        # Forensic investigation
        cls.start_forensic_investigation()
```

## Security Best Practices

### Development Security Guidelines

1. **Secure Coding Practices**
   - Always validate and sanitize input
   - Use parameterized queries
   - Implement proper error handling
   - Follow principle of least privilege
   - Keep dependencies updated

2. **Authentication Security**
   - Implement strong password policies
   - Use multi-factor authentication
   - Implement account lockout mechanisms
   - Use secure session management
   - Implement proper logout functionality

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Implement proper access controls
   - Regular security audits
   - Data backup and recovery plans

4. **Infrastructure Security**
   - Keep systems updated
   - Use firewalls and intrusion detection
   - Implement network segmentation
   - Regular security assessments
   - Monitor system logs

### Security Checklist

#### Pre-Deployment Security Checklist

- [ ] All dependencies updated to latest secure versions
- [ ] Security headers configured in web server
- [ ] HTTPS/TLS properly configured
- [ ] Database access properly restricted
- [ ] Sensitive data encrypted
- [ ] Input validation implemented
- [ ] Rate limiting configured
- [ ] Audit logging enabled
- [ ] Error handling doesn't leak information
- [ ] Security testing completed

#### Regular Security Maintenance

- [ ] Weekly security updates
- [ ] Monthly security assessments
- [ ] Quarterly penetration testing
- [ ] Annual security audit
- [ ] Continuous monitoring alerts configured
- [ ] Incident response plan tested
- [ ] Staff security training completed
- [ ] Backup and recovery tested

### Security Training

All team members should be trained on:

1. **Secure Development Practices**
2. **Common Security Vulnerabilities (OWASP Top 10)**
3. **Data Protection Regulations (GDPR, CCPA)**
4. **Incident Response Procedures**
5. **Social Engineering Awareness**

### Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls/)
- [SANS Security Policies](https://www.sans.org/information-security-policy/)

For security concerns or to report vulnerabilities, please contact: security@rentalsaas.com

