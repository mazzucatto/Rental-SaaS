#!/usr/bin/env python3
"""
Validação Completa do Sistema Rental SaaS
Este script realiza uma validação abrangente de todos os componentes do sistema.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

class SystemValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = []
        
    def log_result(self, component, test, success, message="", details=None):
        """Log validation results."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {component} - {test}"
        if message:
            result += f": {message}"
        print(result)
        
        self.results.append({
            "component": component,
            "test": test,
            "success": success,
            "message": message,
            "details": details or {}
        })
    
    def validate_project_structure(self):
        """Validate project directory structure."""
        print("🏗️  Validating Project Structure")
        print("-" * 40)
        
        required_files = [
            "README.md",
            "CHANGELOG.md",
            "Makefile",
            "docker-compose.yml",
            "docker-compose.dev.yml",
            ".env.example",
            "backend/rental_api/src/main.py",
            "backend/rental_api/requirements.txt",
            "backend/rental_api/Dockerfile",
            "frontend/rental-frontend/package.json",
            "frontend/rental-frontend/src/App.jsx",
            "frontend/rental-frontend/Dockerfile",
            "docs/API.md",
            "docs/INSTALLATION.md",
            "docs/USER_GUIDE.md",
            "docs/DEVELOPMENT.md",
            "docs/SECURITY.md"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_result("Structure", "Required Files", False, 
                          f"Missing {len(missing_files)} files", 
                          {"missing": missing_files})
        else:
            self.log_result("Structure", "Required Files", True, 
                          f"All {len(required_files)} files present")
    
    def validate_backend_dependencies(self):
        """Validate backend Python dependencies."""
        print("\n🐍 Validating Backend Dependencies")
        print("-" * 40)
        
        requirements_file = self.project_root / "backend/rental_api/requirements.txt"
        
        if not requirements_file.exists():
            self.log_result("Backend", "Requirements File", False, "requirements.txt not found")
            return
        
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.read().strip().split('\n')
            
            # Check for essential packages
            essential_packages = [
                'flask', 'sqlalchemy', 'flask-sqlalchemy', 'flask-jwt-extended',
                'flask-cors', 'flask-mail', 'psycopg2-binary', 'redis'
            ]
            
            found_packages = []
            for req in requirements:
                if req.strip() and not req.startswith('#'):
                    package_name = req.split('==')[0].split('>=')[0].split('~=')[0].lower()
                    found_packages.append(package_name)
            
            missing_packages = [pkg for pkg in essential_packages if pkg not in found_packages]
            
            if missing_packages:
                self.log_result("Backend", "Dependencies", False, 
                              f"Missing packages: {missing_packages}")
            else:
                self.log_result("Backend", "Dependencies", True, 
                              f"All {len(essential_packages)} essential packages found")
                
        except Exception as e:
            self.log_result("Backend", "Dependencies", False, str(e))
    
    def validate_frontend_dependencies(self):
        """Validate frontend Node.js dependencies."""
        print("\n⚛️  Validating Frontend Dependencies")
        print("-" * 40)
        
        package_file = self.project_root / "frontend/rental-frontend/package.json"
        
        if not package_file.exists():
            self.log_result("Frontend", "Package File", False, "package.json not found")
            return
        
        try:
            with open(package_file, 'r') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            all_deps = {**dependencies, **dev_dependencies}
            
            # Check for essential packages
            essential_packages = [
                'react', 'react-dom', 'react-router-dom', 'axios',
                'tailwindcss', 'vite', '@vitejs/plugin-react'
            ]
            
            missing_packages = [pkg for pkg in essential_packages if pkg not in all_deps]
            
            if missing_packages:
                self.log_result("Frontend", "Dependencies", False, 
                              f"Missing packages: {missing_packages}")
            else:
                self.log_result("Frontend", "Dependencies", True, 
                              f"All {len(essential_packages)} essential packages found")
                
        except Exception as e:
            self.log_result("Frontend", "Dependencies", False, str(e))
    
    def validate_docker_configuration(self):
        """Validate Docker configuration files."""
        print("\n🐳 Validating Docker Configuration")
        print("-" * 40)
        
        # Check Dockerfiles
        dockerfiles = [
            "backend/rental_api/Dockerfile",
            "frontend/rental-frontend/Dockerfile"
        ]
        
        for dockerfile_path in dockerfiles:
            dockerfile = self.project_root / dockerfile_path
            if dockerfile.exists():
                try:
                    with open(dockerfile, 'r') as f:
                        content = f.read()
                    
                    # Check for security best practices
                    has_user = 'USER ' in content
                    has_healthcheck = 'HEALTHCHECK' in content
                    has_expose = 'EXPOSE' in content
                    
                    issues = []
                    if not has_user:
                        issues.append("No USER directive (security risk)")
                    if not has_healthcheck:
                        issues.append("No HEALTHCHECK directive")
                    if not has_expose:
                        issues.append("No EXPOSE directive")
                    
                    if issues:
                        self.log_result("Docker", f"Dockerfile ({dockerfile_path})", False, 
                                      f"Issues: {', '.join(issues)}")
                    else:
                        self.log_result("Docker", f"Dockerfile ({dockerfile_path})", True, 
                                      "All best practices followed")
                        
                except Exception as e:
                    self.log_result("Docker", f"Dockerfile ({dockerfile_path})", False, str(e))
            else:
                self.log_result("Docker", f"Dockerfile ({dockerfile_path})", False, "File not found")
        
        # Check docker-compose files
        compose_files = ["docker-compose.yml", "docker-compose.dev.yml"]
        
        for compose_file in compose_files:
            compose_path = self.project_root / compose_file
            if compose_path.exists():
                try:
                    with open(compose_path, 'r') as f:
                        content = f.read()
                    
                    # Check for essential services
                    has_backend = 'backend:' in content or 'rental_api' in content
                    has_frontend = 'frontend:' in content or 'rental-frontend' in content
                    has_database = 'postgres:' in content
                    has_cache = 'redis:' in content
                    
                    services = []
                    if has_backend:
                        services.append("backend")
                    if has_frontend:
                        services.append("frontend")
                    if has_database:
                        services.append("database")
                    if has_cache:
                        services.append("cache")
                    
                    if len(services) >= 3:  # At least backend, database, cache
                        self.log_result("Docker", f"Compose ({compose_file})", True, 
                                      f"Services: {', '.join(services)}")
                    else:
                        self.log_result("Docker", f"Compose ({compose_file})", False, 
                                      f"Missing services. Found: {', '.join(services)}")
                        
                except Exception as e:
                    self.log_result("Docker", f"Compose ({compose_file})", False, str(e))
            else:
                self.log_result("Docker", f"Compose ({compose_file})", False, "File not found")
    
    def validate_documentation(self):
        """Validate documentation completeness."""
        print("\n📚 Validating Documentation")
        print("-" * 40)
        
        docs = {
            "README.md": ["installation", "usage", "features", "api"],
            "docs/API.md": ["authentication", "endpoints", "examples"],
            "docs/INSTALLATION.md": ["requirements", "setup", "docker"],
            "docs/USER_GUIDE.md": ["getting started", "features", "tutorial"],
            "docs/DEVELOPMENT.md": ["setup", "architecture", "contributing"],
            "docs/SECURITY.md": ["authentication", "encryption", "best practices"]
        }
        
        for doc_file, required_sections in docs.items():
            doc_path = self.project_root / doc_file
            
            if not doc_path.exists():
                self.log_result("Documentation", doc_file, False, "File not found")
                continue
            
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                missing_sections = []
                for section in required_sections:
                    if section.lower() not in content:
                        missing_sections.append(section)
                
                if missing_sections:
                    self.log_result("Documentation", doc_file, False, 
                                  f"Missing sections: {', '.join(missing_sections)}")
                else:
                    self.log_result("Documentation", doc_file, True, 
                                  f"All {len(required_sections)} sections present")
                    
            except Exception as e:
                self.log_result("Documentation", doc_file, False, str(e))
    
    def validate_security_configuration(self):
        """Validate security configuration."""
        print("\n🔒 Validating Security Configuration")
        print("-" * 40)
        
        # Check .env.example
        env_example = self.project_root / ".env.example"
        if env_example.exists():
            try:
                with open(env_example, 'r') as f:
                    env_content = f.read()
                
                security_vars = [
                    'SECRET_KEY', 'JWT_SECRET_KEY', 'POSTGRES_PASSWORD',
                    'REDIS_PASSWORD', 'MAIL_PASSWORD'
                ]
                
                missing_vars = [var for var in security_vars if var not in env_content]
                
                if missing_vars:
                    self.log_result("Security", "Environment Variables", False, 
                                  f"Missing: {', '.join(missing_vars)}")
                else:
                    self.log_result("Security", "Environment Variables", True, 
                                  "All security variables defined")
                    
            except Exception as e:
                self.log_result("Security", "Environment Variables", False, str(e))
        else:
            self.log_result("Security", "Environment Variables", False, ".env.example not found")
        
        # Check for security headers in nginx config
        nginx_config = self.project_root / "frontend/rental-frontend/nginx.conf"
        if nginx_config.exists():
            try:
                with open(nginx_config, 'r') as f:
                    nginx_content = f.read()
                
                security_headers = [
                    'X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options',
                    'Content-Security-Policy'
                ]
                
                missing_headers = [header for header in security_headers 
                                 if header not in nginx_content]
                
                if missing_headers:
                    self.log_result("Security", "Nginx Headers", False, 
                                  f"Missing: {', '.join(missing_headers)}")
                else:
                    self.log_result("Security", "Nginx Headers", True, 
                                  "All security headers configured")
                    
            except Exception as e:
                self.log_result("Security", "Nginx Headers", False, str(e))
    
    def validate_code_quality(self):
        """Validate code quality and best practices."""
        print("\n🔍 Validating Code Quality")
        print("-" * 40)
        
        # Check Python code structure
        backend_src = self.project_root / "backend/rental_api/src"
        if backend_src.exists():
            python_files = list(backend_src.rglob("*.py"))
            
            if len(python_files) > 0:
                # Check for proper module structure
                has_models = any("models" in str(f) for f in python_files)
                has_routes = any("routes" in str(f) for f in python_files)
                has_config = any("config.py" in str(f) for f in python_files)
                
                structure_score = sum([has_models, has_routes, has_config])
                
                if structure_score == 3:
                    self.log_result("Code Quality", "Backend Structure", True, 
                                  f"Proper MVC structure with {len(python_files)} Python files")
                else:
                    missing = []
                    if not has_models:
                        missing.append("models")
                    if not has_routes:
                        missing.append("routes")
                    if not has_config:
                        missing.append("config")
                    
                    self.log_result("Code Quality", "Backend Structure", False, 
                                  f"Missing: {', '.join(missing)}")
            else:
                self.log_result("Code Quality", "Backend Structure", False, "No Python files found")
        
        # Check React component structure
        frontend_src = self.project_root / "frontend/rental-frontend/src"
        if frontend_src.exists():
            js_files = list(frontend_src.rglob("*.jsx")) + list(frontend_src.rglob("*.js"))
            
            if len(js_files) > 0:
                has_components = any("components" in str(f) for f in js_files)
                has_pages = any("pages" in str(f) for f in js_files)
                has_contexts = any("contexts" in str(f) for f in js_files)
                
                structure_score = sum([has_components, has_pages, has_contexts])
                
                if structure_score >= 2:
                    self.log_result("Code Quality", "Frontend Structure", True, 
                                  f"Good component structure with {len(js_files)} JS/JSX files")
                else:
                    self.log_result("Code Quality", "Frontend Structure", False, 
                                  "Poor component organization")
            else:
                self.log_result("Code Quality", "Frontend Structure", False, "No JS/JSX files found")
    
    def validate_performance_considerations(self):
        """Validate performance optimization features."""
        print("\n⚡ Validating Performance Considerations")
        print("-" * 40)
        
        # Check for database indexing in models
        backend_models = self.project_root / "backend/rental_api/src/models"
        if backend_models.exists():
            model_files = list(backend_models.glob("*.py"))
            
            index_count = 0
            for model_file in model_files:
                try:
                    with open(model_file, 'r') as f:
                        content = f.read()
                    
                    if 'index=True' in content or 'Index(' in content:
                        index_count += 1
                        
                except Exception:
                    pass
            
            if index_count > 0:
                self.log_result("Performance", "Database Indexing", True, 
                              f"Indexes found in {index_count} model files")
            else:
                self.log_result("Performance", "Database Indexing", False, 
                              "No database indexes found")
        
        # Check for caching configuration
        redis_mentioned = False
        config_files = [
            self.project_root / "backend/rental_api/src/config.py",
            self.project_root / "docker-compose.yml"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        content = f.read().lower()
                    
                    if 'redis' in content:
                        redis_mentioned = True
                        break
                        
                except Exception:
                    pass
        
        if redis_mentioned:
            self.log_result("Performance", "Caching", True, "Redis caching configured")
        else:
            self.log_result("Performance", "Caching", False, "No caching configuration found")
        
        # Check for frontend optimization
        vite_config = self.project_root / "frontend/rental-frontend/vite.config.js"
        if vite_config.exists():
            try:
                with open(vite_config, 'r') as f:
                    content = f.read()
                
                has_optimization = 'build' in content or 'rollupOptions' in content
                
                if has_optimization:
                    self.log_result("Performance", "Frontend Build", True, 
                                  "Build optimization configured")
                else:
                    self.log_result("Performance", "Frontend Build", False, 
                                  "No build optimization found")
                    
            except Exception as e:
                self.log_result("Performance", "Frontend Build", False, str(e))
    
    def generate_report(self):
        """Generate validation report."""
        print("\n📊 Validation Report")
        print("=" * 50)
        
        # Count results by component
        components = {}
        for result in self.results:
            component = result['component']
            if component not in components:
                components[component] = {'passed': 0, 'failed': 0, 'total': 0}
            
            components[component]['total'] += 1
            if result['success']:
                components[component]['passed'] += 1
            else:
                components[component]['failed'] += 1
        
        # Print component summary
        for component, stats in components.items():
            success_rate = (stats['passed'] / stats['total']) * 100
            status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 80 else "❌"
            print(f"{status} {component}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Overall summary
        total_tests = len(self.results)
        total_passed = sum(1 for r in self.results if r['success'])
        overall_success_rate = (total_passed / total_tests) * 100
        
        print(f"\n🎯 Overall: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")
        
        if overall_success_rate == 100:
            print("\n🎉 Excellent! All validations passed.")
            print("   The system is ready for production deployment.")
        elif overall_success_rate >= 90:
            print("\n👍 Great! Most validations passed.")
            print("   Minor issues should be addressed before production.")
        elif overall_success_rate >= 80:
            print("\n⚠️  Good progress, but some issues need attention.")
            print("   Address failed validations before deployment.")
        else:
            print("\n❌ Several issues found that need immediate attention.")
            print("   System is not ready for production deployment.")
        
        return overall_success_rate >= 90
    
    def run_validation(self):
        """Run complete system validation."""
        print("🔍 Rental SaaS System Validation")
        print("=" * 50)
        
        self.validate_project_structure()
        self.validate_backend_dependencies()
        self.validate_frontend_dependencies()
        self.validate_docker_configuration()
        self.validate_documentation()
        self.validate_security_configuration()
        self.validate_code_quality()
        self.validate_performance_considerations()
        
        return self.generate_report()

def main():
    """Main function."""
    validator = SystemValidator()
    success = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

