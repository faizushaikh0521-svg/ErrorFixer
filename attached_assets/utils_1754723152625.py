import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def save_uploaded_file(file, folder_type):
    """Save uploaded file and return filename (legacy method)"""
    if file and file.filename:
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{folder_type}_{uuid.uuid4().hex[:8]}_{name}{ext}"
        
        # Create upload directory if it doesn't exist
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder_type)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return f"{folder_type}/{unique_filename}"
    
    return None


def save_crew_document(file, crew_id, document_type, document_category):
    """Save crew document and create database record"""
    from models import CrewDocument, db  # Import here to avoid circular imports
    
    if not file or not file.filename:
        return None
        
    # Generate unique filename
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_filename = f"crew_{uuid.uuid4().hex[:8]}_{name}{ext}"
    
    # Create upload directory if it doesn't exist
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'crew_documents')
    os.makedirs(upload_path, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_path, unique_filename)
    file.save(file_path)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create database record
    doc_record = CrewDocument(
        crew_id=crew_id,
        document_type=document_type,
        document_category=document_category,
        filename=f"crew_documents/{unique_filename}",
        original_filename=file.filename,
        file_size=file_size,
        mime_type=file.content_type or 'application/octet-stream'
    )
    
    db.session.add(doc_record)
    db.session.commit()
    
    return doc_record


def save_multiple_crew_documents(files, crew_id, document_type, document_category):
    """Save multiple files for a document type and return list of saved records"""
    saved_docs = []
    
    if not files:
        return saved_docs
        
    # Handle single file or list of files
    if not isinstance(files, list):
        files = [files]
    
    for file in files:
        if file and file.filename:
            doc_record = save_crew_document(file, crew_id, document_type, document_category)
            if doc_record:
                saved_docs.append(doc_record)
    
    return saved_docs


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
