#!/usr/bin/env python3
"""
Sistema de Testes Abrangente para Rental SaaS
Este script testa todas as funcionalidades principais do sistema.
"""

import sys
import os
import requests
import json
import time
from datetime import datetime, timedelta

# Adicionar o diretório do backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'rental_api'))

class RentalSaaSTester:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.tenant_id = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
    def test_backend_imports(self):
        """Test if all backend modules can be imported."""
        try:
            from src.main import app
            from src.models.user import User, db
            from src.models.tenant import Tenant
            from src.models.rental import RentalItem, Category, Customer, Reservation
            from src.routes.auth import auth_bp
            from src.routes.rental import rental_bp
            from src.routes.tenant import tenant_bp
            
            self.log_test("Backend Module Imports", True, "All modules imported successfully")
            return True
        except Exception as e:
            self.log_test("Backend Module Imports", False, str(e))
            return False
    
    def test_database_creation(self):
        """Test database table creation."""
        try:
            from src.main import app
            from src.models.user import db
            
            with app.app_context():
                db.create_all()
                
                # Check if tables exist using inspector
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                expected_tables = ['tenants', 'users', 'categories', 'rental_items', 
                                 'customers', 'reservations', 'contracts', 'payments']
                
                missing_tables = [table for table in expected_tables if table not in tables]
                
                if missing_tables:
                    self.log_test("Database Creation", False, f"Missing tables: {missing_tables}")
                    return False
                else:
                    self.log_test("Database Creation", True, f"All {len(expected_tables)} tables created")
                    return True
                    
        except Exception as e:
            self.log_test("Database Creation", False, str(e))
            return False
    
    def test_user_registration(self):
        """Test user and tenant registration."""
        try:
            registration_data = {
                "username": "testadmin",
                "email": "test@example.com",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "Admin",
                "phone": "+1234567890",
                "tenant_name": "Test Company",
                "subdomain": "testcompany",
                "timezone": "America/Sao_Paulo",
                "currency": "BRL",
                "language": "pt"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", 
                                       json=registration_data)
            
            if response.status_code == 201:
                data = response.json()
                self.access_token = data.get('access_token')
                self.tenant_id = data.get('tenant', {}).get('id')
                self.user_id = data.get('user', {}).get('id')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                self.log_test("User Registration", True, "User and tenant created successfully")
                return True
            else:
                self.log_test("User Registration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", False, str(e))
            return False
    
    def test_authentication(self):
        """Test user login."""
        try:
            login_data = {
                "email": "test@example.com",
                "password": "TestPassword123!"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                
                if token:
                    self.log_test("Authentication", True, "Login successful")
                    return True
                else:
                    self.log_test("Authentication", False, "No access token received")
                    return False
            else:
                self.log_test("Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, str(e))
            return False
    
    def test_category_management(self):
        """Test category creation and retrieval."""
        try:
            # Create category
            category_data = {
                "name": "Power Tools",
                "description": "Electric and battery-powered tools"
            }
            
            response = self.session.post(f"{self.base_url}/rental/categories", 
                                       json=category_data)
            
            if response.status_code != 201:
                self.log_test("Category Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Get categories
            response = self.session.get(f"{self.base_url}/rental/categories")
            
            if response.status_code == 200:
                categories = response.json().get('categories', [])
                if len(categories) > 0:
                    self.log_test("Category Management", True, f"Created and retrieved {len(categories)} categories")
                    return True
                else:
                    self.log_test("Category Management", False, "No categories found")
                    return False
            else:
                self.log_test("Category Management", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Category Management", False, str(e))
            return False
    
    def test_item_management(self):
        """Test rental item creation and management."""
        try:
            # First get a category ID
            response = self.session.get(f"{self.base_url}/rental/categories")
            if response.status_code != 200:
                self.log_test("Item Management", False, "Could not get categories")
                return False
            
            categories = response.json().get('categories', [])
            if not categories:
                self.log_test("Item Management", False, "No categories available")
                return False
            
            category_id = categories[0]['id']
            
            # Create item
            item_data = {
                "name": "Electric Drill",
                "description": "Professional electric drill with multiple bits",
                "sku": "DRILL-001",
                "category_id": category_id,
                "hourly_price": 15.00,
                "daily_price": 50.00,
                "weekly_price": 300.00,
                "monthly_price": 1000.00,
                "total_quantity": 5,
                "available_quantity": 5,
                "is_active": True
            }
            
            response = self.session.post(f"{self.base_url}/rental/items", json=item_data)
            
            if response.status_code != 201:
                self.log_test("Item Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Get items
            response = self.session.get(f"{self.base_url}/rental/items")
            
            if response.status_code == 200:
                items = response.json().get('items', [])
                if len(items) > 0:
                    self.log_test("Item Management", True, f"Created and retrieved {len(items)} items")
                    return True
                else:
                    self.log_test("Item Management", False, "No items found")
                    return False
            else:
                self.log_test("Item Management", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Item Management", False, str(e))
            return False
    
    def test_customer_management(self):
        """Test customer creation and management."""
        try:
            customer_data = {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "address": "123 Main St, City, State",
                "document_number": "123.456.789-00",
                "document_type": "CPF"
            }
            
            response = self.session.post(f"{self.base_url}/rental/customers", 
                                       json=customer_data)
            
            if response.status_code != 201:
                self.log_test("Customer Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Get customers
            response = self.session.get(f"{self.base_url}/rental/customers")
            
            if response.status_code == 200:
                customers = response.json().get('customers', [])
                if len(customers) > 0:
                    self.log_test("Customer Management", True, f"Created and retrieved {len(customers)} customers")
                    return True
                else:
                    self.log_test("Customer Management", False, "No customers found")
                    return False
            else:
                self.log_test("Customer Management", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Customer Management", False, str(e))
            return False
    
    def test_reservation_system(self):
        """Test reservation creation and management."""
        try:
            # Get items and customers first
            items_response = self.session.get(f"{self.base_url}/rental/items")
            customers_response = self.session.get(f"{self.base_url}/rental/customers")
            
            if items_response.status_code != 200 or customers_response.status_code != 200:
                self.log_test("Reservation System", False, "Could not get items or customers")
                return False
            
            items = items_response.json().get('items', [])
            customers = customers_response.json().get('customers', [])
            
            if not items or not customers:
                self.log_test("Reservation System", False, "No items or customers available")
                return False
            
            # Create reservation
            start_date = datetime.now() + timedelta(days=1)
            end_date = start_date + timedelta(days=2)
            
            reservation_data = {
                "item_id": items[0]['id'],
                "customer_id": customers[0]['id'],
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "quantity": 1,
                "notes": "Test reservation"
            }
            
            response = self.session.post(f"{self.base_url}/rental/reservations", 
                                       json=reservation_data)
            
            if response.status_code != 201:
                self.log_test("Reservation Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Get reservations
            response = self.session.get(f"{self.base_url}/rental/reservations")
            
            if response.status_code == 200:
                reservations = response.json().get('reservations', [])
                if len(reservations) > 0:
                    self.log_test("Reservation System", True, f"Created and retrieved {len(reservations)} reservations")
                    return True
                else:
                    self.log_test("Reservation System", False, "No reservations found")
                    return False
            else:
                self.log_test("Reservation System", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Reservation System", False, str(e))
            return False
    
    def test_dashboard_data(self):
        """Test dashboard data retrieval."""
        try:
            response = self.session.get(f"{self.base_url}/rental/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('stats', {})
                
                if 'total_items' in stats and 'total_customers' in stats:
                    self.log_test("Dashboard Data", True, "Dashboard data retrieved successfully")
                    return True
                else:
                    self.log_test("Dashboard Data", False, "Missing dashboard statistics")
                    return False
            else:
                self.log_test("Dashboard Data", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Data", False, str(e))
            return False
    
    def test_tenant_settings(self):
        """Test tenant settings retrieval and update."""
        try:
            # Get tenant info
            response = self.session.get(f"{self.base_url}/tenants/")
            
            if response.status_code == 200:
                tenant_data = response.json()
                
                # Update tenant settings
                update_data = {
                    "name": "Updated Test Company",
                    "settings": {
                        "timezone": "America/New_York",
                        "currency": "USD"
                    }
                }
                
                response = self.session.put(f"{self.base_url}/tenants/", json=update_data)
                
                if response.status_code == 200:
                    self.log_test("Tenant Settings", True, "Tenant settings updated successfully")
                    return True
                else:
                    self.log_test("Tenant Settings", False, f"Update failed: HTTP {response.status_code}")
                    return False
            else:
                self.log_test("Tenant Settings", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Tenant Settings", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Rental SaaS System Tests")
        print("=" * 50)
        
        # Backend tests (without server)
        self.test_backend_imports()
        self.test_database_creation()
        
        # API tests (require running server)
        print("\n📡 Testing API Endpoints (requires running server)")
        print("-" * 50)
        
        try:
            # Test if server is running
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ Server not running or health check failed")
                print("   Start the server with: cd backend/rental_api && python src/main.py")
                return
        except requests.exceptions.RequestException:
            print("❌ Server not accessible at", self.base_url)
            print("   Start the server with: cd backend/rental_api && python src/main.py")
            return
        
        # Run API tests
        if self.test_user_registration():
            self.test_authentication()
            self.test_category_management()
            self.test_item_management()
            self.test_customer_management()
            self.test_reservation_system()
            self.test_dashboard_data()
            self.test_tenant_settings()
        
        # Print summary
        print("\n📊 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! System is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} tests failed. Check the output above for details.")
            
        return passed == total

def main():
    """Main function to run tests."""
    tester = RentalSaaSTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

