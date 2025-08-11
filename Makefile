# Rental SaaS Makefile
# Comandos para facilitar o desenvolvimento e deploy

.PHONY: help dev prod build clean logs shell test backup restore

# Default target
help:
	@echo "Rental SaaS - Comandos Disponíveis:"
	@echo ""
	@echo "Desenvolvimento:"
	@echo "  make dev          - Inicia ambiente de desenvolvimento"
	@echo "  make dev-build    - Reconstrói e inicia ambiente de desenvolvimento"
	@echo "  make dev-stop     - Para ambiente de desenvolvimento"
	@echo "  make dev-clean    - Remove containers e volumes de desenvolvimento"
	@echo ""
	@echo "Produção:"
	@echo "  make prod         - Inicia ambiente de produção"
	@echo "  make prod-build   - Reconstrói e inicia ambiente de produção"
	@echo "  make prod-stop    - Para ambiente de produção"
	@echo "  make prod-clean   - Remove containers e volumes de produção"
	@echo ""
	@echo "Utilitários:"
	@echo "  make logs         - Mostra logs dos containers"
	@echo "  make logs-f       - Segue logs dos containers em tempo real"
	@echo "  make shell-backend - Acessa shell do container backend"
	@echo "  make shell-db     - Acessa shell do PostgreSQL"
	@echo "  make backup       - Faz backup do banco de dados"
	@echo "  make restore      - Restaura backup do banco de dados"
	@echo "  make test         - Executa testes"
	@echo "  make clean-all    - Remove todos os containers e volumes"

# Development commands
dev:
	@echo "🚀 Iniciando ambiente de desenvolvimento..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Ambiente iniciado!"
	@echo "📊 Adminer: http://localhost:8080"
	@echo "📧 MailHog: http://localhost:8025"

dev-build:
	@echo "🔨 Reconstruindo ambiente de desenvolvimento..."
	docker-compose -f docker-compose.dev.yml up -d --build
	@echo "✅ Ambiente reconstruído e iniciado!"

dev-stop:
	@echo "⏹️  Parando ambiente de desenvolvimento..."
	docker-compose -f docker-compose.dev.yml down

dev-clean:
	@echo "🧹 Limpando ambiente de desenvolvimento..."
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f

# Production commands
prod:
	@echo "🚀 Iniciando ambiente de produção..."
	docker-compose --profile production up -d
	@echo "✅ Ambiente de produção iniciado!"
	@echo "🌐 Frontend: http://localhost"
	@echo "🔧 API: http://localhost:5000"

prod-build:
	@echo "🔨 Reconstruindo ambiente de produção..."
	docker-compose --profile production up -d --build
	@echo "✅ Ambiente de produção reconstruído!"

prod-stop:
	@echo "⏹️  Parando ambiente de produção..."
	docker-compose down

prod-clean:
	@echo "🧹 Limpando ambiente de produção..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Utility commands
logs:
	docker-compose logs

logs-f:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f postgres

shell-backend:
	docker-compose exec backend /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh

shell-db:
	docker-compose exec postgres psql -U rental_user -d rental_saas

# Database operations
backup:
	@echo "💾 Fazendo backup do banco de dados..."
	mkdir -p backups
	docker-compose exec postgres pg_dump -U rental_user rental_saas > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup salvo em backups/"

restore:
	@echo "📥 Para restaurar um backup, execute:"
	@echo "docker-compose exec -T postgres psql -U rental_user -d rental_saas < backups/seu_backup.sql"

# Testing
test:
	@echo "🧪 Executando testes..."
	docker-compose exec backend python -m pytest tests/ -v

test-coverage:
	@echo "🧪 Executando testes com cobertura..."
	docker-compose exec backend python -m pytest tests/ --cov=src --cov-report=html

# Database migrations
migrate:
	@echo "🔄 Executando migrações do banco..."
	docker-compose exec backend python -c "from src.main import app, db; app.app_context().push(); db.create_all()"

# Clean everything
clean-all:
	@echo "🧹 Removendo todos os containers, volumes e imagens..."
	docker-compose -f docker-compose.yml down -v --remove-orphans
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -af --volumes
	@echo "✅ Limpeza completa realizada!"

# Setup environment
setup:
	@echo "⚙️  Configurando ambiente..."
	@if [ ! -f .env ]; then \
		echo "📝 Criando arquivo .env..."; \
		cp .env.example .env; \
		echo "✅ Arquivo .env criado! Edite as configurações conforme necessário."; \
	else \
		echo "ℹ️  Arquivo .env já existe."; \
	fi

# Health check
health:
	@echo "🏥 Verificando saúde dos containers..."
	docker-compose ps
	@echo ""
	@echo "🔍 Status dos serviços:"
	@curl -s http://localhost:5000/api/health || echo "❌ Backend não está respondendo"
	@curl -s http://localhost/health || echo "❌ Frontend não está respondendo"

# Show container stats
stats:
	docker stats --no-stream

# View container sizes
sizes:
	docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

