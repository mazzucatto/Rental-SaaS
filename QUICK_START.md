# 🚀 Guia de Início Rápido - Rental SaaS

Este guia irá ajudá-lo a configurar e executar o Rental SaaS em poucos minutos.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Docker** (versão 20.10+)
- **Docker Compose** (versão 2.0+)
- **Git** (para clonar o repositório)

### Verificar Instalação

```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar Git
git --version
```

## 🏃‍♂️ Início Rápido (5 minutos)

### 1. Clonar o Repositório

```bash
git clone <repository-url>
cd rental-saas
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações (opcional para desenvolvimento)
nano .env
```

### 3. Iniciar o Sistema

```bash
# Iniciar ambiente de desenvolvimento
make dev

# OU usar Docker Compose diretamente
docker-compose -f docker-compose.dev.yml up -d
```

### 4. Acessar o Sistema

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **Adminer (DB)**: http://localhost:8080
- **MailHog (Email)**: http://localhost:8025

### 5. Primeiro Login

1. Acesse http://localhost:3000
2. Clique em "Registrar"
3. Preencha os dados da empresa e usuário administrador
4. Faça login com as credenciais criadas

## 🎯 Primeiros Passos no Sistema

### 1. Configurar sua Empresa

1. **Acesse Configurações** → Configurações da Empresa
2. **Configure**:
   - Nome da empresa
   - Timezone
   - Moeda
   - Horário de funcionamento

### 2. Criar Categorias de Itens

1. **Acesse** → Inventário → Categorias
2. **Clique** em "Nova Categoria"
3. **Exemplos**:
   - Ferramentas Elétricas
   - Equipamentos de Construção
   - Veículos
   - Equipamentos de Festa

### 3. Adicionar Itens de Locação

1. **Acesse** → Inventário → Itens
2. **Clique** em "Novo Item"
3. **Preencha**:
   - Nome do item
   - Descrição
   - SKU
   - Categoria
   - Preços (hora/dia/semana/mês)
   - Quantidade disponível

### 4. Cadastrar Clientes

1. **Acesse** → Clientes
2. **Clique** em "Novo Cliente"
3. **Preencha** os dados do cliente

### 5. Criar sua Primeira Reserva

1. **Acesse** → Reservas
2. **Clique** em "Nova Reserva"
3. **Selecione**:
   - Cliente
   - Item
   - Datas de início e fim
   - Quantidade
4. **Confirme** a reserva

## 🛠️ Comandos Úteis

### Gerenciamento do Sistema

```bash
# Iniciar ambiente de desenvolvimento
make dev

# Iniciar ambiente de produção
make prod

# Parar todos os serviços
make stop

# Ver logs em tempo real
make logs

# Fazer backup do banco de dados
make backup

# Restaurar backup
make restore

# Limpar dados de desenvolvimento
make clean
```

### Desenvolvimento

```bash
# Instalar dependências do backend
cd backend/rental_api
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Instalar dependências do frontend
cd frontend/rental-frontend
npm install
# ou
pnpm install
```

### Testes

```bash
# Executar testes do sistema
python test_system.py

# Validar configuração completa
python validate_system.py

# Testes do backend
cd backend/rental_api
python -m pytest

# Testes do frontend
cd frontend/rental-frontend
npm test
```

## 🔧 Configurações Avançadas

### Configurar Email (Opcional)

Edite o arquivo `.env`:

```env
# Configurações de Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
MAIL_DEFAULT_SENDER=seu-email@gmail.com
```

### Configurar Domínio Personalizado

Para produção, configure seu domínio:

```env
# Domínio principal
DOMAIN=suaempresa.com

# Subdomínio para tenants
TENANT_SUBDOMAIN_FORMAT={subdomain}.suaempresa.com

# CORS Origins
CORS_ORIGINS=https://suaempresa.com,https://*.suaempresa.com
```

### Configurar SSL/HTTPS

Para produção com SSL:

1. **Obtenha certificados SSL** (Let's Encrypt recomendado)
2. **Configure nginx** com os certificados
3. **Atualize docker-compose.yml** para produção

## 📊 Monitoramento

### Health Checks

```bash
# Verificar saúde dos serviços
curl http://localhost:5000/api/health

# Verificar status do banco
curl http://localhost:5000/api/health/db

# Verificar status do cache
curl http://localhost:5000/api/health/cache
```

### Logs

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Métricas

Acesse o dashboard para ver:
- Número de reservas ativas
- Receita do mês
- Taxa de utilização de itens
- Clientes ativos

## 🚨 Solução de Problemas

### Problemas Comuns

#### 1. Porta já em uso

```bash
# Verificar portas em uso
netstat -tulpn | grep :3000
netstat -tulpn | grep :5000

# Parar processos se necessário
sudo kill -9 <PID>
```

#### 2. Erro de permissão no Docker

```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar sessão ou executar
newgrp docker
```

#### 3. Banco de dados não conecta

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Verificar logs do banco
docker-compose logs postgres

# Recriar banco se necessário
docker-compose down -v
docker-compose up -d
```

#### 4. Frontend não carrega

```bash
# Verificar se o build foi bem-sucedido
cd frontend/rental-frontend
npm run build

# Verificar logs do frontend
docker-compose logs frontend
```

### Resetar Sistema

Para começar do zero:

```bash
# Parar todos os serviços
make stop

# Remover volumes (CUIDADO: apaga todos os dados)
docker-compose down -v

# Remover imagens
docker-compose down --rmi all

# Iniciar novamente
make dev
```

## 📞 Suporte

### Documentação Adicional

- **[README.md](README.md)** - Visão geral completa
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** - Instalação detalhada
- **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** - Manual do usuário
- **[docs/API.md](docs/API.md)** - Documentação da API
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Guia de desenvolvimento

### Recursos Úteis

- **Logs do Sistema**: `docker-compose logs -f`
- **Banco de Dados**: Acesse via Adminer em http://localhost:8080
- **Emails de Teste**: Visualize em http://localhost:8025
- **API Testing**: Use Postman ou curl com a documentação da API

### Contato

Para suporte técnico ou dúvidas:
- Consulte a documentação completa
- Verifique os logs do sistema
- Execute os scripts de validação

---

## 🎉 Parabéns!

Você agora tem o Rental SaaS funcionando! 

**Próximos passos recomendados:**
1. Explore todas as funcionalidades
2. Configure sua empresa e itens
3. Teste o fluxo completo de locação
4. Personalize conforme suas necessidades
5. Configure para produção quando estiver pronto

**Aproveite seu novo sistema de gestão de locações!** 🚀

