from app import db
from datetime import datetime
from flask_login import UserMixin
import secrets
import hashlib


class Admin(UserMixin, db.Model):
    """Admin user model for dashboard access"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class CrewMember(db.Model):
    """Crew member model for registration and tracking"""
    __tablename__ = 'crew_members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    rank = db.Column(db.String(64), nullable=False)
    passport = db.Column(db.String(32), unique=True, nullable=False)
    
    # Enhanced fields
    nationality = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    years_experience = db.Column(db.Integer, nullable=False)
    last_vessel_type = db.Column(db.String(128))
    availability_date = db.Column(db.Date, nullable=False)
    available_port_city = db.Column(db.String(128))  # Available Port / City for Joining
    mobile_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # Emergency contact
    emergency_contact_name = db.Column(db.String(128))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(64))
    
    # File upload fields - Identity documents
    passport_file = db.Column(db.String(255))
    government_id_file = db.Column(db.String(255))  # Government ID (Aadhaar / PAN / SSN) - Optional
    photo_file = db.Column(db.String(255))
    
    # Medical documents
    medical_certificate_file = db.Column(db.String(255))
    yellow_fever_file = db.Column(db.String(255))  # Yellow Fever (optional)
    
    # Professional documents
    cdc_file = db.Column(db.String(255))  # CDC/Seaman Book
    coc_cop_file = db.Column(db.String(255))  # Certificate of Competency/Proficiency
    stcw_certificates_file = db.Column(db.String(255))  # STCW Certificates
    gmdss_dce_file = db.Column(db.String(255))  # GMDSS or DCE (if applicable)
    
    # Other documents
    resume_file = db.Column(db.String(255))
    sea_agreement_file = db.Column(db.String(255))  # SEA Agreement (Optional)
    
    # Profile access token for secure private access
    profile_token = db.Column(db.String(128), unique=True)
    
    # Status and notes
    status = db.Column(db.Integer, default=0)  # 0=Registered, 1=Screening, 2=Documents Verified, 3=Approved, -1=Rejected, -2=Flagged
    admin_notes = db.Column(db.Text)
    screening_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrewMember {self.name} ({self.passport})>'
    
    def get_status_name(self):
        """Get the human-readable status name"""
        status_names = {
            0: "Registered",
            1: "Screening",
            2: "Documents Verified", 
            3: "Approved",
            -1: "Rejected",
            -2: "Flagged"
        }
        return status_names.get(self.status, "Unknown")
    
    def get_status_class(self):
        """Get Bootstrap class for status"""
        status_classes = {
            0: "secondary",
            1: "warning",
            2: "info",
            3: "success",
            -1: "danger",
            -2: "dark"
        }
        return status_classes.get(self.status, "secondary")


class CrewDocument(db.Model):
    """Document storage model for crew members - supports multiple files per category"""
    __tablename__ = 'crew_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    crew_id = db.Column(db.Integer, db.ForeignKey('crew_members.id'), nullable=False)
    document_type = db.Column(db.String(64), nullable=False)  # passport, cdc, medical, etc.
    document_category = db.Column(db.String(32), nullable=False)  # identity, medical, professional, other
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship back to crew member
    crew_member = db.relationship('CrewMember', backref=db.backref('documents', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<CrewDocument {self.document_type} for crew {self.crew_id}>'
    
    def get_file_size_formatted(self):
        """Format file size in human readable format"""
        if not self.file_size:
            return "Unknown size"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"
    
    def generate_profile_token(self):
        """Generate a secure token for profile access"""
        if not self.profile_token:
            # Generate a secure random token
            random_bytes = secrets.token_bytes(32)
            # Create a hash that includes crew ID for uniqueness
            token_data = f"{self.id}_{self.passport}_{random_bytes.hex()}"
            self.profile_token = hashlib.sha256(token_data.encode()).hexdigest()
            db.session.commit()
        return self.profile_token
    
    def get_document_categories(self):
        """Get documents organized by categories with their status (new multi-file system)"""
        categories = {
            'identity': {
                'name': 'Identity Documents',
                'documents': [
                    {'type': 'passport', 'name': 'Passport Copy', 'required': True},
                    {'type': 'government_id', 'name': 'Government ID (Aadhaar / PAN / SSN)', 'required': False},
                    {'type': 'photo', 'name': 'Photo (Passport Size)', 'required': True},
                ]
            },
            'medical': {
                'name': 'Medical Documents',
                'documents': [
                    {'type': 'medical_certificate', 'name': 'Medical Certificate', 'required': True},
                    {'type': 'yellow_fever', 'name': 'Yellow Fever Certificate', 'required': False},
                ]
            },
            'professional': {
                'name': 'Professional Documents',
                'documents': [
                    {'type': 'cdc', 'name': 'CDC (Seaman Book)', 'required': True},
                    {'type': 'coc_cop', 'name': 'COC/COP Certificate', 'required': True},
                    {'type': 'stcw_certificates', 'name': 'STCW Certificates', 'required': True},
                    {'type': 'gmdss_dce', 'name': 'GMDSS/DCE Certificate', 'required': False},
                ]
            },
            'other': {
                'name': 'Other Documents',
                'documents': [
                    {'type': 'resume', 'name': 'Resume/CV', 'required': True},
                    {'type': 'sea_agreement', 'name': 'SEA Agreement', 'required': False},
                ]
            }
        }
        
        # Check status of each document type using the new documents table
        for category_key, category in categories.items():
            for doc in category['documents']:
                # Get all documents of this type for this crew member
                doc_files = CrewDocument.query.filter_by(
                    crew_id=self.id, 
                    document_type=doc['type']
                ).order_by(CrewDocument.upload_date.desc()).all()
                
                doc['files'] = doc_files
                doc['uploaded'] = len(doc_files) > 0
                doc['status'] = 'complete' if doc['uploaded'] else 'missing'
                doc['count'] = len(doc_files)
        
        return categories
    
    def get_required_documents(self):
        """Get list of required documents with their status (updated for new system)"""
        categories = self.get_document_categories()
        documents = []
        
        for category in categories.values():
            documents.extend(category['documents'])
        
        return documents
    
    def get_documents_by_category(self, category_name):
        """Get all documents for a specific category"""
        return CrewDocument.query.filter_by(
            crew_id=self.id, 
            document_category=category_name
        ).order_by(CrewDocument.upload_date.desc()).all()
    
    def get_all_documents(self):
        """Get all documents for this crew member sorted by upload date"""
        return CrewDocument.query.filter_by(
            crew_id=self.id
        ).order_by(CrewDocument.upload_date.desc()).all()
    
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage based on new document system"""
        categories = self.get_document_categories()
        required_docs = []
        uploaded_docs = []
        
        for category in categories.values():
            for doc in category['documents']:
                if doc['required']:
                    required_docs.append(doc)
                    if doc['uploaded']:
                        uploaded_docs.append(doc)
        
        if not required_docs:
            return 100
        
        return int((len(uploaded_docs) / len(required_docs)) * 100)
    
    def is_profile_complete(self):
        """Check if profile is 100% complete"""
        return self.get_profile_completion_percentage() == 100


class StaffMember(db.Model):
    """Staff member model for offshore/office staff registration"""
    __tablename__ = 'staff_members'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    email_or_whatsapp = db.Column(db.String(128), nullable=False)
    position_applying = db.Column(db.String(128), nullable=False)
    department = db.Column(db.String(32), nullable=False)  # Ops, HR, Tech, Crewing
    years_experience = db.Column(db.Integer, nullable=False)
    current_employer = db.Column(db.String(128))
    location = db.Column(db.String(128), nullable=False)
    availability_date = db.Column(db.Date, nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    
    # Additional information
    education = db.Column(db.String(255))
    certifications = db.Column(db.Text)
    salary_expectation = db.Column(db.String(64))
    
    # File upload fields
    resume_file = db.Column(db.String(255))
    photo_file = db.Column(db.String(255))
    
    # Status and notes
    status = db.Column(db.Integer, default=1)  # 1=Screening, 3=Approved, -1=Rejected
    admin_notes = db.Column(db.Text)
    screening_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StaffMember {self.full_name} ({self.position_applying})>'
    
    def get_status_name(self):
        """Get the human-readable status name"""
        status_names = {
            1: "Screening",
            3: "Approved",
            -1: "Rejected"
        }
        return status_names.get(self.status, "Unknown")
    
    def get_status_class(self):
        """Get Bootstrap class for status"""
        status_classes = {
            1: "warning",
            3: "success",
            -1: "danger"
        }
        return status_classes.get(self.status, "warning")
