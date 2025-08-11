# Docker Setup - Rental SaaS

Este documento explica como executar o Rental SaaS usando Docker e Docker Compose.

## Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Make (opcional, para usar comandos simplificados)

## Configuração Inicial

1. **Clone o repositório e navegue até a pasta:**
   ```bash
   cd rental-saas
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   ```
   
   Edite o arquivo `.env` com suas configurações:
   - Senhas do banco de dados e Redis
   - Chaves secretas do Flask e JWT
   - Configurações de email SMTP
   - URLs e domínios

## Ambientes Disponíveis

### Desenvolvimento

Para desenvolvimento local com hot-reload e ferramentas de debug:

```bash
# Usando Make (recomendado)
make setup  # Cria arquivo .env se não existir
make dev    # Inicia ambiente de desenvolvimento

# Ou usando Docker Compose diretamente
docker-compose -f docker-compose.dev.yml up -d
```

**Serviços disponíveis em desenvolvimento:**
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Adminer (DB Admin): `http://localhost:8080`
- MailHog (Email Testing): `http://localhost:8025`

### Produção

Para ambiente de produção completo:

```bash
# Usando Make (recomendado)
make prod

# Ou usando Docker Compose diretamente
docker-compose --profile production up -d
```

**Serviços disponíveis em produção:**
- Frontend: `http://localhost` (porta 80)
- Backend API: `http://localhost:5000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Nginx (opcional): `http://localhost:8080` e `https://localhost:443`

## Comandos Úteis

### Usando Make (Recomendado)

```bash
# Desenvolvimento
make dev          # Inicia ambiente de desenvolvimento
make dev-build    # Reconstrói e inicia ambiente de desenvolvimento
make dev-stop     # Para ambiente de desenvolvimento
make dev-clean    # Remove containers e volumes de desenvolvimento

# Produção
make prod         # Inicia ambiente de produção
make prod-build   # Reconstrói e inicia ambiente de produção
make prod-stop    # Para ambiente de produção
make prod-clean   # Remove containers e volumes de produção

# Utilitários
make logs         # Mostra logs dos containers
make logs-f       # Segue logs em tempo real
make shell-backend # Acessa shell do container backend
make shell-db     # Acessa shell do PostgreSQL
make backup       # Faz backup do banco de dados
make test         # Executa testes
make health       # Verifica saúde dos serviços
```

### Usando Docker Compose Diretamente

```bash
# Desenvolvimento
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml down

# Produção
docker-compose --profile production up -d
docker-compose down

# Logs
docker-compose logs -f [service_name]

# Shell nos containers
docker-compose exec backend /bin/bash
docker-compose exec postgres psql -U rental_user -d rental_saas

# Rebuild
docker-compose up -d --build
```

## Estrutura dos Containers

### Backend (Flask API)
- **Imagem:** Python 3.11 slim
- **Porta:** 5000
- **Volumes:** uploads para arquivos
- **Dependências:** PostgreSQL, Redis

### Frontend (React + Nginx)
- **Imagem:** Node 20 (build) + Nginx Alpine (runtime)
- **Porta:** 80
- **Build:** Multi-stage para otimização
- **Proxy:** Nginx com proxy reverso para API

### PostgreSQL
- **Imagem:** PostgreSQL 15 Alpine
- **Porta:** 5432
- **Volume:** Dados persistentes
- **Inicialização:** Script SQL automático

### Redis
- **Imagem:** Redis 7 Alpine
- **Porta:** 6379
- **Volume:** Dados persistentes
- **Configuração:** AOF habilitado

### Nginx (Produção)
- **Imagem:** Nginx Alpine
- **Portas:** 80, 443
- **SSL:** Configuração para certificados
- **Proxy:** Load balancer e reverse proxy

## Volumes Persistentes

- `postgres_data`: Dados do PostgreSQL
- `redis_data`: Dados do Redis
- `backend_uploads`: Arquivos enviados pelo backend

## Rede

Todos os containers estão na rede `rental_network` com subnet `172.20.0.0/16`.

## Monitoramento e Saúde

### Health Checks

Todos os serviços principais têm health checks configurados:

```bash
# Verificar status
docker-compose ps

# Health check manual
curl http://localhost:5000/api/health
curl http://localhost/health
```

### Logs

```bash
# Todos os serviços
make logs

# Serviço específico
make logs-backend
make logs-frontend
make logs-db

# Tempo real
make logs-f
```

## Backup e Restore

### Backup Automático

```bash
make backup
```

Cria backup em `backups/backup_YYYYMMDD_HHMMSS.sql`

### Restore Manual

```bash
# Restaurar backup específico
docker-compose exec -T postgres psql -U rental_user -d rental_saas < backups/backup_20240101_120000.sql
```

## Desenvolvimento Local

Para desenvolvimento com hot-reload:

1. **Inicie apenas os serviços de infraestrutura:**
   ```bash
   make dev
   ```

2. **Execute backend localmente:**
   ```bash
   cd backend/rental_api
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   python src/main.py
   ```

3. **Execute frontend localmente:**
   ```bash
   cd frontend/rental-frontend
   pnpm install
   pnpm run dev
   ```

## Troubleshooting

### Problemas Comuns

1. **Porta já em uso:**
   ```bash
   # Verificar processos usando a porta
   sudo lsof -i :5000
   sudo lsof -i :80
   
   # Parar containers
   make dev-stop
   make prod-stop
   ```

2. **Problemas de permissão:**
   ```bash
   # Recriar volumes
   make dev-clean
   make dev
   ```

3. **Banco de dados não conecta:**
   ```bash
   # Verificar logs do PostgreSQL
   docker-compose logs postgres
   
   # Verificar health check
   docker-compose exec postgres pg_isready -U rental_user
   ```

4. **Frontend não carrega:**
   ```bash
   # Verificar build do frontend
   docker-compose logs frontend
   
   # Rebuild frontend
   docker-compose up -d --build frontend
   ```

### Limpeza Completa

```bash
# Remove tudo (cuidado!)
make clean-all

# Ou manualmente
docker-compose down -v --remove-orphans
docker system prune -af --volumes
```

## Configurações de Produção

### Variáveis Importantes

```env
# Segurança
SECRET_KEY=sua-chave-super-secreta-minimo-32-caracteres
JWT_SECRET_KEY=sua-chave-jwt-secreta-minimo-32-caracteres

# Banco de dados
POSTGRES_PASSWORD=senha-forte-do-banco

# Redis
REDIS_PASSWORD=senha-forte-do-redis

# Email
MAIL_SERVER=smtp.seuprovedor.com
MAIL_USERNAME=seu-email@dominio.com
MAIL_PASSWORD=sua-senha-de-app
```

### SSL/HTTPS

Para habilitar HTTPS em produção:

1. Coloque seus certificados em `nginx/ssl/`
2. Configure `nginx/conf.d/default.conf`
3. Inicie com perfil de produção:
   ```bash
   docker-compose --profile production up -d
   ```

## Performance

### Otimizações

- Imagens multi-stage para menor tamanho
- Health checks para monitoramento
- Volumes nomeados para performance
- Nginx com gzip e cache
- PostgreSQL com configurações otimizadas

### Monitoramento

```bash
# Estatísticas dos containers
make stats

# Tamanho das imagens
make sizes

# Uso de recursos
docker system df
```

