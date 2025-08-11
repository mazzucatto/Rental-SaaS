# Development Guide - Rental SaaS

This guide provides comprehensive information for developers working on the Rental SaaS project.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [Database Management](#database-management)
- [Testing](#testing)
- [Code Standards](#code-standards)
- [Contributing](#contributing)
- [Deployment](#deployment)

## Development Environment Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Git**
- **PostgreSQL 15+** (for local development)
- **Redis 7+** (for local development)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/your-username/rental-saas.git
cd rental-saas

# Start infrastructure services
make dev

# Setup backend
cd backend/rental_api
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python src/main.py

# Setup frontend (new terminal)
cd frontend/rental-frontend
pnpm install
pnpm run dev
```

### IDE Configuration

#### VS Code

Recommended extensions:
- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- ESLint
- Docker
- GitLens

#### Settings

```json
{
  "python.defaultInterpreterPath": "./backend/rental_api/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Project Structure

```
rental-saas/
├── backend/
│   └── rental_api/
│       ├── src/
│       │   ├── models/          # Database models
│       │   ├── routes/          # API endpoints
│       │   ├── services/        # Business logic
│       │   ├── utils/           # Utility functions
│       │   ├── config.py        # Configuration
│       │   └── main.py          # Application entry point
│       ├── tests/               # Backend tests
│       ├── migrations/          # Database migrations
│       ├── requirements.txt     # Python dependencies
│       └── Dockerfile          # Backend container
├── frontend/
│   └── rental-frontend/
│       ├── src/
│       │   ├── components/      # React components
│       │   ├── pages/          # Page components
│       │   ├── contexts/       # React contexts
│       │   ├── hooks/          # Custom hooks
│       │   ├── lib/            # Utilities and API
│       │   └── styles/         # CSS and styling
│       ├── public/             # Static assets
│       ├── package.json        # Node dependencies
│       └── Dockerfile          # Frontend container
├── docs/                       # Documentation
├── database/                   # Database scripts
├── nginx/                      # Nginx configuration
├── docker-compose.yml          # Production compose
├── docker-compose.dev.yml      # Development compose
├── Makefile                    # Development commands
└── README.md                   # Project overview
```

## Architecture Overview

### System Architecture

The application follows a modern three-tier architecture:

1. **Presentation Layer** (React Frontend)
2. **Application Layer** (Flask API)
3. **Data Layer** (PostgreSQL + Redis)

### Design Patterns

- **MVC Pattern**: Model-View-Controller separation
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic encapsulation
- **Factory Pattern**: Object creation
- **Observer Pattern**: Event handling

### Multi-Tenancy

The system implements row-level multi-tenancy:
- Each tenant has isolated data
- Tenant ID is included in all database queries
- Middleware ensures tenant isolation
- Shared infrastructure with logical separation

## Backend Development

### Flask Application Structure

```python
# src/main.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(rental_bp)
    
    return app
```

### Models

Models use SQLAlchemy ORM with multi-tenant support:

```python
# src/models/base.py
class TenantMixin:
    tenant_id = db.Column(db.String(36), nullable=False, index=True)
    
    @classmethod
    def query_for_tenant(cls, tenant_id):
        return cls.query.filter_by(tenant_id=tenant_id)

# src/models/rental.py
class RentalItem(db.Model, TenantMixin):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    # ... other fields
```

### API Routes

Routes are organized by feature using Flask Blueprints:

```python
# src/routes/rental.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

rental_bp = Blueprint('rental', __name__)

@rental_bp.route('/items', methods=['GET'])
@jwt_required()
def get_items():
    tenant_id = get_jwt_identity()['tenant_id']
    items = RentalItem.query_for_tenant(tenant_id).all()
    return jsonify([item.to_dict() for item in items])
```

### Services

Business logic is encapsulated in service classes:

```python
# src/services/rental_service.py
class RentalService:
    @staticmethod
    def create_reservation(tenant_id, item_id, customer_id, start_date, end_date):
        # Check availability
        if not RentalService.is_available(item_id, start_date, end_date):
            raise ValueError("Item not available for selected dates")
        
        # Calculate pricing
        price = RentalService.calculate_price(item_id, start_date, end_date)
        
        # Create reservation
        reservation = Reservation(
            tenant_id=tenant_id,
            item_id=item_id,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            final_amount=price
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        return reservation
```

### Authentication & Authorization

JWT-based authentication with role-based access control:

```python
# src/utils/auth.py
from functools import wraps
from flask_jwt_extended import get_jwt_identity

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            if permission not in current_user.get('permissions', []):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@rental_bp.route('/items', methods=['POST'])
@jwt_required()
@require_permission('manage_items')
def create_item():
    # Implementation
```

### Error Handling

Centralized error handling with custom exceptions:

```python
# src/utils/exceptions.py
class RentalException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

class ItemNotAvailableException(RentalException):
    def __init__(self, message="Item not available"):
        super().__init__(message, 422)

# src/main.py
@app.errorhandler(RentalException)
def handle_rental_exception(e):
    return jsonify({'error': e.message}), e.status_code
```

### Configuration Management

Environment-based configuration:

```python
# src/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

## Frontend Development

### React Application Structure

```jsx
// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/items" element={<Items />} />
            <Route path="/reservations" element={<Reservations />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}
```

### State Management

Using React Context for global state:

```jsx
// src/contexts/AuthContext.jsx
import { createContext, useContext, useReducer } from 'react';

const AuthContext = createContext();

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false
      };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: false
  });

  return (
    <AuthContext.Provider value={{ ...state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

### API Integration

Centralized API client:

```javascript
// src/lib/api.js
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

class ApiClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Request interceptor for auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(credentials) {
    const response = await this.client.post('/auth/login', credentials);
    return response.data;
  }

  // Rental methods
  async getItems(params = {}) {
    const response = await this.client.get('/rental/items', { params });
    return response.data;
  }

  async createItem(itemData) {
    const response = await this.client.post('/rental/items', itemData);
    return response.data;
  }
}

export default new ApiClient();
```

### Component Development

Reusable components with TypeScript-like prop validation:

```jsx
// src/components/ItemCard.jsx
import PropTypes from 'prop-types';

const ItemCard = ({ item, onEdit, onDelete }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold">{item.name}</h3>
        <span className={`px-2 py-1 rounded text-sm ${
          item.status === 'available' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {item.status}
        </span>
      </div>
      
      <p className="text-gray-600 mb-4">{item.description}</p>
      
      <div className="flex justify-between items-center">
        <span className="text-xl font-bold">${item.daily_price}/day</span>
        <div className="space-x-2">
          <button 
            onClick={() => onEdit(item)}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Edit
          </button>
          <button 
            onClick={() => onDelete(item.id)}
            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

ItemCard.propTypes = {
  item: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    daily_price: PropTypes.number.isRequired,
    status: PropTypes.string.isRequired
  }).isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired
};

export default ItemCard;
```

### Custom Hooks

Reusable logic with custom hooks:

```jsx
// src/hooks/useApi.js
import { useState, useEffect } from 'react';
import api from '../lib/api';

export const useApi = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.client.get(endpoint, options);
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  return { data, loading, error, refetch: fetchData };
};

// Usage
const Items = () => {
  const { data: items, loading, error, refetch } = useApi('/rental/items');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {items?.items?.map(item => (
        <ItemCard key={item.id} item={item} />
      ))}
    </div>
  );
};
```

## Database Management

### Migrations

Database schema changes are managed through Flask-Migrate:

```bash
# Create migration
flask db migrate -m "Add new column to items table"

# Apply migration
flask db upgrade

# Downgrade migration
flask db downgrade
```

### Seeding Data

Development data seeding:

```python
# src/utils/seed.py
def seed_database():
    # Create default tenant
    tenant = Tenant(
        name="Demo Company",
        subdomain="demo",
        settings={"currency": "USD", "timezone": "UTC"}
    )
    db.session.add(tenant)
    
    # Create admin user
    admin = User(
        tenant_id=tenant.id,
        username="admin",
        email="admin@demo.com",
        role="admin"
    )
    admin.set_password("password")
    db.session.add(admin)
    
    # Create sample categories
    categories = [
        Category(tenant_id=tenant.id, name="Power Tools"),
        Category(tenant_id=tenant.id, name="Construction Equipment")
    ]
    db.session.add_all(categories)
    
    db.session.commit()
```

### Query Optimization

Best practices for database queries:

```python
# Use eager loading to avoid N+1 queries
items = RentalItem.query.options(
    joinedload(RentalItem.category),
    joinedload(RentalItem.reservations)
).filter_by(tenant_id=tenant_id).all()

# Use pagination for large datasets
items = RentalItem.query.filter_by(tenant_id=tenant_id).paginate(
    page=page, per_page=20, error_out=False
)

# Use database functions for aggregations
revenue = db.session.query(
    func.sum(Payment.amount)
).filter(
    Payment.tenant_id == tenant_id,
    Payment.status == 'paid'
).scalar()
```

## Testing

### Backend Testing

Using pytest for backend tests:

```python
# tests/conftest.py
import pytest
from src.main import create_app, db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Create test user and get token
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

# tests/test_rental.py
def test_create_item(client, auth_headers):
    response = client.post('/api/rental/items', 
        json={
            'name': 'Test Item',
            'daily_price': 50.00,
            'category_id': 'category-id'
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json['item']['name'] == 'Test Item'
```

### Frontend Testing

Using Jest and React Testing Library:

```jsx
// src/components/__tests__/ItemCard.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import ItemCard from '../ItemCard';

const mockItem = {
  id: '1',
  name: 'Test Item',
  description: 'Test description',
  daily_price: 50.00,
  status: 'available'
};

test('renders item information', () => {
  const onEdit = jest.fn();
  const onDelete = jest.fn();
  
  render(<ItemCard item={mockItem} onEdit={onEdit} onDelete={onDelete} />);
  
  expect(screen.getByText('Test Item')).toBeInTheDocument();
  expect(screen.getByText('$50/day')).toBeInTheDocument();
  expect(screen.getByText('available')).toBeInTheDocument();
});

test('calls onEdit when edit button is clicked', () => {
  const onEdit = jest.fn();
  const onDelete = jest.fn();
  
  render(<ItemCard item={mockItem} onEdit={onEdit} onDelete={onDelete} />);
  
  fireEvent.click(screen.getByText('Edit'));
  expect(onEdit).toHaveBeenCalledWith(mockItem);
});
```

### Integration Testing

End-to-end testing with Cypress:

```javascript
// cypress/e2e/rental_flow.cy.js
describe('Rental Flow', () => {
  beforeEach(() => {
    cy.login('admin@demo.com', 'password');
  });

  it('creates a new reservation', () => {
    cy.visit('/reservations');
    cy.get('[data-cy=new-reservation]').click();
    
    cy.get('[data-cy=customer-select]').select('John Doe');
    cy.get('[data-cy=item-select]').select('Electric Drill');
    cy.get('[data-cy=start-date]').type('2024-01-15');
    cy.get('[data-cy=end-date]').type('2024-01-17');
    
    cy.get('[data-cy=submit]').click();
    
    cy.get('[data-cy=success-message]').should('contain', 'Reservation created');
  });
});
```

## Code Standards

### Python Code Style

Following PEP 8 with additional conventions:

```python
# Use type hints
def calculate_price(item_id: str, start_date: datetime, end_date: datetime) -> float:
    """Calculate rental price based on duration."""
    pass

# Use docstrings
class RentalService:
    """Service class for rental operations."""
    
    @staticmethod
    def create_reservation(tenant_id: str, **kwargs) -> Reservation:
        """
        Create a new reservation.
        
        Args:
            tenant_id: The tenant identifier
            **kwargs: Reservation parameters
            
        Returns:
            Created reservation instance
            
        Raises:
            ItemNotAvailableException: If item is not available
        """
        pass

# Use constants
class ReservationStatus:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
```

### JavaScript Code Style

Using ESLint and Prettier:

```javascript
// Use const/let instead of var
const API_BASE_URL = process.env.REACT_APP_API_URL;

// Use arrow functions
const calculateTotal = (items) => {
  return items.reduce((sum, item) => sum + item.price, 0);
};

// Use destructuring
const { name, price, status } = item;

// Use template literals
const message = `Item ${name} costs $${price}`;

// Use async/await
const fetchItems = async () => {
  try {
    const response = await api.getItems();
    return response.data;
  } catch (error) {
    console.error('Failed to fetch items:', error);
    throw error;
  }
};
```

### Git Workflow

Using Conventional Commits:

```bash
# Feature development
git checkout -b feature/add-payment-integration
git commit -m "feat: add stripe payment integration"
git commit -m "test: add payment integration tests"
git commit -m "docs: update payment documentation"

# Bug fixes
git commit -m "fix: resolve reservation date validation issue"

# Breaking changes
git commit -m "feat!: change API response format for items endpoint"
```

### Code Review Guidelines

1. **Functionality**: Does the code work as intended?
2. **Readability**: Is the code easy to understand?
3. **Performance**: Are there any performance issues?
4. **Security**: Are there any security vulnerabilities?
5. **Testing**: Are there adequate tests?
6. **Documentation**: Is the code properly documented?

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Write tests**
5. **Update documentation**
6. **Submit a pull request**

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Issue Templates

```markdown
## Bug Report
**Describe the bug**
A clear description of the bug

**To Reproduce**
Steps to reproduce the behavior

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 91]
- Version: [e.g. 1.0.0]
```

## Deployment

### CI/CD Pipeline

GitHub Actions workflow:

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend/rental_api
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend/rental_api
        pytest
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install frontend dependencies
      run: |
        cd frontend/rental-frontend
        npm install
    
    - name: Run frontend tests
      run: |
        cd frontend/rental-frontend
        npm test
    
    - name: Build frontend
      run: |
        cd frontend/rental-frontend
        npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Deployment script
        echo "Deploying to production..."
```

### Environment Management

Different configurations for different environments:

```bash
# Development
export FLASK_ENV=development
export DEBUG=true
export DATABASE_URL=postgresql://localhost/rental_saas_dev

# Staging
export FLASK_ENV=staging
export DEBUG=false
export DATABASE_URL=postgresql://staging-db/rental_saas_staging

# Production
export FLASK_ENV=production
export DEBUG=false
export DATABASE_URL=postgresql://prod-db/rental_saas_prod
```

### Monitoring and Logging

Application monitoring setup:

```python
# src/utils/monitoring.py
import logging
from flask import request, g
import time

def setup_logging(app):
    if not app.debug:
        # Production logging
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    app.logger.info(f'{request.method} {request.path} - {response.status_code} - {duration:.3f}s')
    return response
```

This development guide provides the foundation for contributing to the Rental SaaS project. For specific questions or clarifications, please refer to the project documentation or reach out to the development team.

