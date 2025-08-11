# API Documentation - Rental SaaS

## Overview

The Rental SaaS API is a RESTful web service that provides comprehensive functionality for managing rental operations. The API follows REST principles and uses JSON for data exchange.

**Base URL:** `http://localhost:5000/api`

**Authentication:** JWT Bearer Token

**Content-Type:** `application/json`

## Authentication

### Register New Tenant and Admin User

Creates a new tenant (company) and admin user account.

```http
POST /auth/register
```

**Request Body:**
```json
{
  "username": "admin",
  "email": "admin@company.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "tenant_name": "My Rental Company",
  "subdomain": "mycompany",
  "timezone": "America/Sao_Paulo",
  "currency": "BRL",
  "language": "pt"
}
```

**Response:**
```json
{
  "message": "User and tenant created successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@company.com",
    "role": "admin"
  },
  "tenant": {
    "id": "uuid",
    "name": "My Rental Company",
    "subdomain": "mycompany"
  }
}
```

### Login

Authenticates a user and returns access tokens.

```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "admin@company.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@company.com",
    "role": "admin"
  },
  "tenant": {
    "id": "uuid",
    "name": "My Rental Company"
  }
}
```

### Refresh Token

Refreshes the access token using a refresh token.

```http
POST /auth/refresh
```

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Get Current User

Returns information about the currently authenticated user.

```http
GET /auth/me
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "admin",
    "permissions": ["manage_items", "manage_reservations"]
  },
  "tenant": {
    "id": "uuid",
    "name": "My Rental Company",
    "subdomain": "mycompany"
  }
}
```

## Rental Items

### List Items

Retrieves a paginated list of rental items.

```http
GET /rental/items
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 10, max: 100)
- `search` (string): Search term for item name or SKU
- `category_id` (uuid): Filter by category
- `status` (string): Filter by status (available, rented, maintenance, retired)
- `is_active` (boolean): Filter by active status

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Electric Drill",
      "description": "Professional electric drill with multiple bits",
      "sku": "DRILL-001",
      "category": {
        "id": "uuid",
        "name": "Power Tools"
      },
      "hourly_price": 15.00,
      "daily_price": 50.00,
      "weekly_price": 300.00,
      "monthly_price": 1000.00,
      "total_quantity": 5,
      "available_quantity": 3,
      "status": "available",
      "is_active": true,
      "images": ["url1", "url2"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3
  }
}
```

### Get Item

Retrieves a specific rental item by ID.

```http
GET /rental/items/{id}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Electric Drill",
  "description": "Professional electric drill with multiple bits",
  "sku": "DRILL-001",
  "category": {
    "id": "uuid",
    "name": "Power Tools"
  },
  "hourly_price": 15.00,
  "daily_price": 50.00,
  "weekly_price": 300.00,
  "monthly_price": 1000.00,
  "total_quantity": 5,
  "available_quantity": 3,
  "min_rental_hours": 4,
  "max_rental_days": 30,
  "requires_deposit": true,
  "deposit_amount": 200.00,
  "specifications": {
    "power": "800W",
    "chuck_size": "13mm",
    "weight": "2.5kg"
  },
  "status": "available",
  "is_active": true,
  "images": ["url1", "url2"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Create Item

Creates a new rental item.

```http
POST /rental/items
```

**Request Body:**
```json
{
  "name": "Electric Drill",
  "description": "Professional electric drill with multiple bits",
  "sku": "DRILL-001",
  "category_id": "uuid",
  "hourly_price": 15.00,
  "daily_price": 50.00,
  "weekly_price": 300.00,
  "monthly_price": 1000.00,
  "total_quantity": 5,
  "available_quantity": 5,
  "min_rental_hours": 4,
  "max_rental_days": 30,
  "requires_deposit": true,
  "deposit_amount": 200.00,
  "specifications": {
    "power": "800W",
    "chuck_size": "13mm",
    "weight": "2.5kg"
  },
  "is_active": true
}
```

**Response:**
```json
{
  "message": "Item created successfully",
  "item": {
    "id": "uuid",
    "name": "Electric Drill",
    "sku": "DRILL-001",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Update Item

Updates an existing rental item.

```http
PUT /rental/items/{id}
```

**Request Body:** Same as create item

**Response:**
```json
{
  "message": "Item updated successfully",
  "item": {
    "id": "uuid",
    "name": "Electric Drill",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### Delete Item

Soft deletes a rental item (sets is_active to false).

```http
DELETE /rental/items/{id}
```

**Response:**
```json
{
  "message": "Item deleted successfully"
}
```

## Categories

### List Categories

Retrieves all categories for the tenant.

```http
GET /rental/categories
```

**Response:**
```json
{
  "categories": [
    {
      "id": "uuid",
      "name": "Power Tools",
      "description": "Electric and battery-powered tools",
      "parent_id": null,
      "children": [
        {
          "id": "uuid",
          "name": "Drills",
          "parent_id": "parent_uuid"
        }
      ],
      "item_count": 15,
      "is_active": true
    }
  ]
}
```

### Create Category

Creates a new category.

```http
POST /rental/categories
```

**Request Body:**
```json
{
  "name": "Power Tools",
  "description": "Electric and battery-powered tools",
  "parent_id": null
}
```

## Customers

### List Customers

Retrieves a paginated list of customers.

```http
GET /rental/customers
```

**Query Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `search` (string): Search term for customer name or email

**Response:**
```json
{
  "customers": [
    {
      "id": "uuid",
      "customer_code": "CLI202400001",
      "full_name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "+1234567890",
      "address": "123 Main St, City, State",
      "document_number": "123.456.789-00",
      "document_type": "CPF",
      "is_active": true,
      "total_reservations": 5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 50,
    "pages": 5
  }
}
```

### Create Customer

Creates a new customer.

```http
POST /rental/customers
```

**Request Body:**
```json
{
  "full_name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State",
  "document_number": "123.456.789-00",
  "document_type": "CPF",
  "birth_date": "1990-01-01",
  "notes": "VIP customer"
}
```

## Reservations

### List Reservations

Retrieves a paginated list of reservations.

```http
GET /rental/reservations
```

**Query Parameters:**
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `search` (string): Search term
- `status` (string): Filter by status
- `start_date` (date): Filter by start date
- `end_date` (date): Filter by end date
- `customer_id` (uuid): Filter by customer
- `item_id` (uuid): Filter by item

**Response:**
```json
{
  "reservations": [
    {
      "id": "uuid",
      "reservation_code": "RES00001",
      "item": {
        "id": "uuid",
        "name": "Electric Drill",
        "sku": "DRILL-001"
      },
      "customer": {
        "id": "uuid",
        "full_name": "Jane Smith",
        "email": "jane@example.com"
      },
      "start_date": "2024-01-15T09:00:00Z",
      "end_date": "2024-01-17T17:00:00Z",
      "quantity": 1,
      "base_amount": 100.00,
      "additional_fees": 10.00,
      "discount_amount": 5.00,
      "final_amount": 105.00,
      "deposit_amount": 200.00,
      "status": "confirmed",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10
  }
}
```

### Create Reservation

Creates a new reservation.

```http
POST /rental/reservations
```

**Request Body:**
```json
{
  "item_id": "uuid",
  "customer_id": "uuid",
  "start_date": "2024-01-15T09:00:00Z",
  "end_date": "2024-01-17T17:00:00Z",
  "quantity": 1,
  "additional_fees": 10.00,
  "discount_amount": 5.00,
  "notes": "Customer requested early pickup"
}
```

**Response:**
```json
{
  "message": "Reservation created successfully",
  "reservation": {
    "id": "uuid",
    "reservation_code": "RES00001",
    "final_amount": 105.00,
    "status": "pending"
  }
}
```

### Confirm Reservation

Confirms a pending reservation.

```http
POST /rental/reservations/{id}/confirm
```

**Response:**
```json
{
  "message": "Reservation confirmed successfully",
  "reservation": {
    "id": "uuid",
    "status": "confirmed",
    "confirmed_at": "2024-01-01T00:00:00Z"
  }
}
```

## Calendar

### Get Calendar Events

Retrieves reservation events for calendar display.

```http
GET /rental/calendar
```

**Query Parameters:**
- `start_date` (date): Start date for calendar view
- `end_date` (date): End date for calendar view

**Response:**
```json
{
  "events": [
    {
      "id": "uuid",
      "title": "Electric Drill - Jane Smith",
      "start": "2024-01-15T09:00:00Z",
      "end": "2024-01-17T17:00:00Z",
      "status": "confirmed",
      "item_id": "uuid",
      "customer_id": "uuid",
      "reservation_id": "uuid"
    }
  ]
}
```

## Dashboard

### Get Dashboard Data

Retrieves dashboard statistics and recent activity.

```http
GET /rental/dashboard
```

**Response:**
```json
{
  "stats": {
    "total_items": 50,
    "active_items": 45,
    "total_customers": 100,
    "reservations": {
      "pending": 5,
      "confirmed": 15,
      "active": 8,
      "completed": 200,
      "cancelled": 10
    },
    "revenue": {
      "today": 500.00,
      "this_week": 2500.00,
      "this_month": 10000.00,
      "this_year": 120000.00
    }
  },
  "recent_reservations": [
    {
      "id": "uuid",
      "reservation_code": "RES00001",
      "customer": {
        "full_name": "Jane Smith"
      },
      "item": {
        "name": "Electric Drill"
      },
      "status": "confirmed",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "upcoming_reservations": [
    {
      "id": "uuid",
      "reservation_code": "RES00002",
      "customer": {
        "full_name": "John Doe"
      },
      "item": {
        "name": "Concrete Mixer"
      },
      "start_date": "2024-01-15T09:00:00Z",
      "status": "confirmed"
    }
  ]
}
```

## Tenant Management

### Get Tenant Information

Retrieves current tenant information.

```http
GET /tenants/
```

**Response:**
```json
{
  "id": "uuid",
  "name": "My Rental Company",
  "subdomain": "mycompany",
  "settings": {
    "timezone": "America/Sao_Paulo",
    "currency": "BRL",
    "language": "pt",
    "business_hours": {
      "monday": {"open": "08:00", "close": "18:00"},
      "tuesday": {"open": "08:00", "close": "18:00"}
    }
  },
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Tenant

Updates tenant information and settings.

```http
PUT /tenants/
```

**Request Body:**
```json
{
  "name": "My Updated Rental Company",
  "settings": {
    "timezone": "America/New_York",
    "currency": "USD",
    "language": "en"
  }
}
```

### Get Tenant Statistics

Retrieves detailed statistics for the tenant.

```http
GET /tenants/stats
```

**Response:**
```json
{
  "overview": {
    "total_items": 50,
    "total_customers": 100,
    "total_reservations": 500,
    "total_revenue": 50000.00
  },
  "monthly_stats": [
    {
      "month": "2024-01",
      "reservations": 45,
      "revenue": 4500.00,
      "new_customers": 8
    }
  ],
  "top_items": [
    {
      "item_id": "uuid",
      "name": "Electric Drill",
      "rental_count": 25,
      "revenue": 1250.00
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": {
    "email": ["This field is required"],
    "password": ["Password must be at least 6 characters"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "message": "Please provide a valid access token"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions",
  "message": "You don't have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "message": "The requested item was not found"
}
```

### 422 Unprocessable Entity
```json
{
  "error": "Business logic error",
  "message": "Item is not available for the selected dates"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints:** 5 requests per minute per IP
- **General endpoints:** 100 requests per minute per user
- **File upload endpoints:** 10 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with the following parameters:

- `page`: Page number (starts at 1)
- `per_page`: Items per page (default: 10, max: 100)

Pagination information is included in the response:
```json
{
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering and Searching

Many list endpoints support filtering and searching:

- Use query parameters for filtering (e.g., `status=active`)
- Use the `search` parameter for text search
- Multiple filters can be combined
- Search is case-insensitive and searches multiple fields

## Date and Time Format

All dates and times are in ISO 8601 format with UTC timezone:
```
2024-01-01T00:00:00Z
```

When sending dates in requests, you can use:
- ISO 8601 format: `2024-01-01T00:00:00Z`
- Date only: `2024-01-01` (assumes start of day)

## File Uploads

File upload endpoints accept multipart/form-data:

```http
POST /rental/items/{id}/images
Content-Type: multipart/form-data

file: [binary data]
```

Supported file types:
- Images: JPG, PNG, GIF (max 5MB each)
- Documents: PDF (max 10MB)

## Webhooks

The system supports webhooks for real-time notifications:

### Webhook Events
- `reservation.created`
- `reservation.confirmed`
- `reservation.cancelled`
- `payment.completed`
- `item.low_stock`

### Webhook Payload
```json
{
  "event": "reservation.created",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "reservation": {
      "id": "uuid",
      "reservation_code": "RES00001"
    }
  }
}
```

## SDK and Libraries

Official SDKs are available for:
- JavaScript/TypeScript
- Python
- PHP
- C#

Community SDKs:
- Ruby
- Go
- Java

## Support

For API support:
- Documentation: [API Docs](https://docs.rentalsaas.com)
- Support Email: api-support@rentalsaas.com
- GitHub Issues: [GitHub Repository](https://github.com/rental-saas/api)
- Discord: [Developer Community](https://discord.gg/rentalsaas)

