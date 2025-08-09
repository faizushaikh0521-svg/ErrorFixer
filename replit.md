# Maricheck - Maritime Crew Management System

## Overview

Maricheck is a Flask-based web application designed for managing maritime crew member registrations and staff recruitment. The system provides a dual-interface design with public-facing registration forms for crew members and shore staff, alongside a protected admin dashboard for managing applications, tracking statuses, and handling document uploads. The platform serves as a comprehensive recruitment and crew management solution for the maritime industry.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for dynamic content rendering
- **UI Framework**: Bootstrap 5 with custom maritime theme using navy blue, sea green, and gold color scheme
- **Icons**: Font Awesome 6.4.0 for consistent iconography throughout the application
- **Typography**: Google Fonts (Inter) for professional, readable typography
- **Responsive Design**: Mobile-first approach using Bootstrap grid system with custom CSS optimizations
- **Interactive Elements**: File upload handling, form validation feedback, and copy-to-clipboard functionality
- **JavaScript**: Custom maricheck.js for enhanced user interactions, auto-hiding alerts, and form loading states

### Backend Architecture
- **Framework**: Flask (Python web framework) with modular route organization
- **Database**: SQLAlchemy ORM with SQLite default configuration (production-ready for PostgreSQL migration)
- **Authentication**: Flask-Login for session-based admin authentication with simple username/password system
- **Forms**: Flask-WTF with WTForms for comprehensive form handling, validation, and CSRF protection
- **Security**: Werkzeug password hashing for admin credentials, secure file uploads with unique naming using UUID
- **File Management**: Organized upload system with categorized storage (passport, CDC, resume, photo, medical certificates)
- **Configuration**: Environment-based configuration for database URL and session secrets

### Database Schema Design
- **Admin Model**: Simple authentication table with username and password hash for dashboard access
- **CrewMember Model**: Comprehensive crew registration with personal info, professional details, emergency contacts, and file upload references
- **CrewDocument Model**: Document storage system supporting multiple files per category with metadata tracking
- **Status Tracking**: Built-in status enumeration system (Registered, Screening, Documents Verified, Approved, Rejected, Flagged)
- **File References**: Database stores file paths rather than binary data for better performance and scalability
- **Unique Constraints**: Passport numbers enforced as unique identifiers for crew members

### Key Architectural Decisions
- **Dual Interface Separation**: Public registration portal and protected admin dashboard serve different user needs
- **Session-Based Authentication**: Simple admin login without complex role-based access control suitable for small teams
- **File Upload Strategy**: Secure filename generation using UUID prefixes and organized folder structure in static/uploads
- **Database Agnostic Design**: SQLite for development with easy PostgreSQL migration for production environments
- **Status Management**: Centralized status tracking with visual indicators and filtering capabilities in admin interface
- **Privacy Controls**: Private profile links with tokens for crew members, exclusively managed through admin panel

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework for Python with extensions for SQLAlchemy, Login, and WTF forms
- **SQLAlchemy**: ORM for database operations with support for multiple database backends
- **Werkzeug**: WSGI utilities for secure file handling and password hashing
- **WTForms**: Form validation and rendering library with Flask-WTF integration

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design and UI components
- **Font Awesome 6.4.0**: Icon library for consistent visual elements
- **Google Fonts**: Web fonts service for Inter font family

### Database Support
- **SQLite**: Default database for development and small deployments
- **PostgreSQL Ready**: Architecture supports PostgreSQL migration for production scaling

### File Storage
- **Local File System**: Static file storage in organized directory structure
- **UUID**: Unique filename generation for secure file uploads
- **Multiple Format Support**: PDF, JPG, JPEG, PNG files for document uploads