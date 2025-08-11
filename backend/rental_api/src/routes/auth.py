from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
import uuid

from src.models.user import db, User
from src.models.tenant import Tenant

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário e tenant."""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['username', 'email', 'password', 'tenant_name', 'subdomain']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se o subdomínio já existe
        existing_tenant = Tenant.query.filter_by(subdomain=data['subdomain']).first()
        if existing_tenant:
            return jsonify({'error': 'Subdomínio já está em uso'}), 400
        
        # Criar tenant
        tenant = Tenant.create_tenant(
            name=data['tenant_name'],
            subdomain=data['subdomain'],
            timezone=data.get('timezone', 'UTC'),
            currency=data.get('currency', 'USD'),
            language=data.get('language', 'en')
        )
        
        db.session.add(tenant)
        db.session.flush()  # Para obter o ID do tenant
        
        # Verificar se o email já existe para este tenant
        existing_user = User.query.filter_by(
            tenant_id=tenant.id, 
            email=data['email']
        ).first()
        if existing_user:
            return jsonify({'error': 'Email já está em uso neste tenant'}), 400
        
        # Criar usuário administrador
        user = User(
            tenant_id=tenant.id,
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role='admin'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Criar tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'tenant_id': tenant.id, 'role': user.role}
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Usuário e tenant criados com sucesso',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'tenant': tenant.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica um usuário."""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Buscar usuário por email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Usuário inativo'}), 401
        
        # Verificar se o tenant está ativo
        tenant = Tenant.query.get(user.tenant_id)
        if not tenant or not tenant.is_active:
            return jsonify({'error': 'Tenant inativo'}), 401
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Criar tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'tenant_id': user.tenant_id, 'role': user.role}
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'tenant': tenant.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renova o token de acesso."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'Usuário não encontrado ou inativo'}), 401
        
        # Criar novo token de acesso
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'tenant_id': user.tenant_id, 'role': user.role}
        )
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Retorna informações do usuário atual."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        tenant = Tenant.query.get(user.tenant_id)
        
        return jsonify({
            'user': user.to_dict(),
            'tenant': tenant.to_dict() if tenant else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout do usuário (invalidar token)."""
    # Em uma implementação completa, você adicionaria o token a uma blacklist
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Altera a senha do usuário."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
        
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Senha atual incorreta'}), 401
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Solicita reset de senha."""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email é obrigatório'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user:
            # Aqui você implementaria o envio de email com token de reset
            # Por enquanto, apenas retornamos sucesso
            pass
        
        # Sempre retorna sucesso por segurança (não revelar se email existe)
        return jsonify({'message': 'Se o email existir, você receberá instruções para reset'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

