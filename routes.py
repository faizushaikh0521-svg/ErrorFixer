import os
import csv
from io import StringIO
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, make_response, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from app import app, db
from models import Admin, CrewMember, StaffMember, CrewDocument
from forms import CrewRegistrationForm, StaffRegistrationForm, TrackingForm, AdminLoginForm, CrewProfileDocumentForm
from utils import save_uploaded_file, save_multiple_crew_documents


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/register/crew', methods=['GET', 'POST'])
def register_crew():
    """Crew member registration"""
    form = CrewRegistrationForm()
    
    if form.validate_on_submit():
        # Check if passport already exists
        existing_crew = CrewMember.query.filter_by(passport=form.passport.data.upper() if form.passport.data else '').first()
        if existing_crew:
            flash('A crew member with this passport number already exists.', 'error')
            return render_template('register_crew.html', form=form)
        
        # Create new crew member
        crew_member = CrewMember(
            name=form.name.data,
            nationality=form.nationality.data,
            date_of_birth=form.date_of_birth.data,
            mobile_number=form.mobile_number.data,
            email=form.email.data,
            rank=form.rank.data,
            passport=form.passport.data.upper() if form.passport.data else '',
            years_experience=form.years_experience.data,
            last_vessel_type=form.last_vessel_type.data,
            availability_date=form.availability_date.data,
            available_port_city=form.available_port_city.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            emergency_contact_relationship=form.emergency_contact_relationship.data
        )
        
        # Handle file uploads - Core documents only for registration
        file_fields = ['passport_file', 'cdc_file', 'resume_file', 'photo_file', 'medical_certificate_file']
        for field_name in file_fields:
            file_field = getattr(form, field_name)
            if file_field.data:
                filename = save_uploaded_file(file_field.data, 'crew')
                setattr(crew_member, field_name, filename)
        
        db.session.add(crew_member)
        db.session.commit()
        
        # Generate profile token for secure access
        crew_member.generate_profile_token()
        
        flash('Registration successful! Your application has been submitted. Our team will review your profile and contact you with the next steps.', 'success')
        return redirect(url_for('track_status', passport=crew_member.passport))
    
    return render_template('register_crew.html', form=form)


@app.route('/register/staff', methods=['GET', 'POST'])
def register_staff():
    """Staff member registration"""
    form = StaffRegistrationForm()
    
    if form.validate_on_submit():
        # Create new staff member
        staff_member = StaffMember(
            full_name=form.full_name.data,
            email_or_whatsapp=form.email_or_whatsapp.data,
            mobile_number=form.mobile_number.data,
            location=form.location.data,
            position_applying=form.position_applying.data,
            department=form.department.data,
            years_experience=form.years_experience.data,
            current_employer=form.current_employer.data,
            availability_date=form.availability_date.data,
            education=form.education.data,
            certifications=form.certifications.data,
            salary_expectation=form.salary_expectation.data
        )
        
        # Handle file uploads
        file_fields = ['resume_file', 'photo_file']
        for field_name in file_fields:
            file_field = getattr(form, field_name)
            if file_field.data:
                filename = save_uploaded_file(file_field.data, 'staff')
                setattr(staff_member, field_name, filename)
        
        db.session.add(staff_member)
        db.session.commit()
        
        flash('Registration successful! Your application has been submitted.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register_staff.html', form=form)


@app.route('/track', methods=['GET', 'POST'])
def track_status():
    """Track application status"""
    form = TrackingForm()
    crew_member = None
    passport_param = request.args.get('passport')
    
    if passport_param:
        form.passport.data = passport_param
    
    if form.validate_on_submit() or passport_param:
        passport = form.passport.data or passport_param
        crew_member = CrewMember.query.filter_by(passport=passport.upper() if passport else '').first()
        if not crew_member:
            flash('No crew member found with this passport number.', 'error')
    
    return render_template('track_status.html', form=form, crew_member=crew_member)


@app.route('/my-profile/<int:crew_id>-<token>')
def crew_private_profile(crew_id, token):
    """Crew member private profile for document uploads"""
    crew_member = CrewMember.query.get_or_404(crew_id)
    
    # Verify token
    if not crew_member.profile_token or crew_member.profile_token != token:
        flash('Invalid or expired profile link.', 'error')
        return redirect(url_for('index'))
    
    # Initialize document form
    document_form = CrewProfileDocumentForm()
    
    # Handle document uploads
    if document_form.validate_on_submit():
        updated_docs = []
        
        # Define document categories mapping
        document_categories = {
            'passport': {'category': 'identity', 'name': 'Passport Copy'},
            'government_id': {'category': 'identity', 'name': 'Government ID'},
            'photo': {'category': 'identity', 'name': 'Photo'},
            'medical_certificate': {'category': 'medical', 'name': 'Medical Certificate'},
            'yellow_fever': {'category': 'medical', 'name': 'Yellow Fever Certificate'},
            'cdc': {'category': 'professional', 'name': 'CDC (Seaman Book)'},
            'coc_cop': {'category': 'professional', 'name': 'COC/COP Certificate'},
            'stcw_certificates': {'category': 'professional', 'name': 'STCW Certificates'},
            'gmdss_dce': {'category': 'professional', 'name': 'GMDSS/DCE Certificate'},
            'resume': {'category': 'other', 'name': 'Resume/CV'},
            'sea_agreement': {'category': 'other', 'name': 'SEA Agreement'},
        }
        
        # Handle all document fields
        for field_name, doc_info in document_categories.items():
            file_field = getattr(document_form, field_name)
            if file_field.data:
                # Save multiple files for this document type
                saved_docs = save_multiple_crew_documents(
                    file_field.data, 
                    crew_member.id, 
                    field_name, 
                    doc_info['category']
                )
                if saved_docs:
                    count = len(saved_docs)
                    updated_docs.append(f"{doc_info['name']} ({count} file{'s' if count > 1 else ''})")
        
        if updated_docs:
            crew_member.updated_at = datetime.utcnow()
            db.session.commit()
            flash(f'Successfully uploaded: {", ".join(updated_docs)}', 'success')
        else:
            flash('No files were selected for upload.', 'warning')
        
        return redirect(url_for('crew_private_profile', crew_id=crew_id, token=token))
    
    return render_template('crew_private_profile.html', 
                         crew_member=crew_member, 
                         document_form=document_form)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.password_hash and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html', form=form)


@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    # Get statistics
    total_crew = CrewMember.query.count()
    total_staff = StaffMember.query.count()
    crew_screening = CrewMember.query.filter_by(status=1).count()
    staff_screening = StaffMember.query.filter_by(status=1).count()
    crew_approved = CrewMember.query.filter_by(status=3).count()
    staff_approved = StaffMember.query.filter_by(status=3).count()
    
    # Get recent registrations
    recent_crew = CrewMember.query.order_by(CrewMember.created_at.desc()).limit(5).all()
    recent_staff = StaffMember.query.order_by(StaffMember.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_crew=total_crew,
                         total_staff=total_staff,
                         crew_screening=crew_screening,
                         staff_screening=staff_screening,
                         crew_approved=crew_approved,
                         staff_approved=staff_approved,
                         recent_crew=recent_crew,
                         recent_staff=recent_staff)


@app.route('/admin/crew')
@login_required
def crew_list():
    """Crew member list"""
    status_filter = request.args.get('status')
    search = request.args.get('search', '')
    
    query = CrewMember.query
    
    if status_filter:
        query = query.filter(CrewMember.status == int(status_filter))
    
    if search:
        query = query.filter(
            db.or_(
                CrewMember.name.ilike(f'%{search}%'),
                CrewMember.passport.ilike(f'%{search}%'),
                CrewMember.rank.ilike(f'%{search}%')
            )
        )
    
    crew_members = query.order_by(CrewMember.created_at.desc()).all()
    
    return render_template('admin/crew_list.html', crew_members=crew_members, search=search, status_filter=status_filter)


@app.route('/admin/staff')
@login_required
def staff_list():
    """Staff member list"""
    status_filter = request.args.get('status')
    search = request.args.get('search', '')
    
    query = StaffMember.query
    
    if status_filter:
        query = query.filter(StaffMember.status == int(status_filter))
    
    if search:
        query = query.filter(
            db.or_(
                StaffMember.full_name.ilike(f'%{search}%'),
                StaffMember.position_applying.ilike(f'%{search}%'),
                StaffMember.department.ilike(f'%{search}%')
            )
        )
    
    staff_members = query.order_by(StaffMember.created_at.desc()).all()
    
    return render_template('admin/staff_list.html', staff_members=staff_members, search=search, status_filter=status_filter)


@app.route('/admin/crew/<int:crew_id>')
@login_required
def crew_profile(crew_id):
    """Crew member profile"""
    crew_member = CrewMember.query.get_or_404(crew_id)
    return render_template('admin/crew_profile.html', crew_member=crew_member)


@app.route('/admin/staff/<int:staff_id>')
@login_required
def staff_profile(staff_id):
    """Staff member profile"""
    staff_member = StaffMember.query.get_or_404(staff_id)
    return render_template('admin/staff_profile.html', staff_member=staff_member)


@app.route('/admin/crew/<int:crew_id>/update_status', methods=['POST'])
@login_required
def update_crew_status(crew_id):
    """Update crew member status"""
    crew_member = CrewMember.query.get_or_404(crew_id)
    action = request.form.get('action')
    notes = request.form.get('notes', '')
    
    if action == 'approve':
        crew_member.status = 3
        crew_member.admin_notes = notes
        flash('Crew member approved successfully.', 'success')
    elif action == 'reject':
        crew_member.status = -1
        crew_member.admin_notes = notes
        flash('Crew member rejected.', 'warning')
    elif action == 'flag':
        crew_member.status = -2
        crew_member.admin_notes = notes
        flash('Crew member flagged for review.', 'info')
    
    crew_member.updated_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('crew_profile', crew_id=crew_id))


@app.route('/admin/staff/<int:staff_id>/update_status', methods=['POST'])
@login_required
def update_staff_status(staff_id):
    """Update staff member status"""
    staff_member = StaffMember.query.get_or_404(staff_id)
    action = request.form.get('action')
    notes = request.form.get('notes', '')
    
    if action == 'approve':
        staff_member.status = 3
        staff_member.admin_notes = notes
        flash('Staff member approved successfully.', 'success')
    elif action == 'reject':
        staff_member.status = -1
        staff_member.admin_notes = notes
        flash('Staff member rejected.', 'warning')
    
    staff_member.updated_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('staff_profile', staff_id=staff_id))


@app.route('/admin/crew/<int:crew_id>/export_csv')
@login_required
def export_crew_csv(crew_id):
    """Export crew member data as CSV"""
    crew_member = CrewMember.query.get_or_404(crew_id)
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'Name', 'Rank', 'Passport', 'Nationality', 'Date of Birth', 
        'Years Experience', 'Mobile', 'Email', 'Status', 'Created At'
    ])
    
    # Write crew data
    writer.writerow([
        crew_member.name,
        crew_member.rank,
        crew_member.passport,
        crew_member.nationality,
        crew_member.date_of_birth.strftime('%Y-%m-%d') if crew_member.date_of_birth else '',
        crew_member.years_experience,
        crew_member.mobile_number,
        crew_member.email,
        crew_member.get_status_name(),
        crew_member.created_at.strftime('%Y-%m-%d %H:%M:%S')
    ])
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=crew_{crew_member.passport}.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response


@app.route('/admin/crew/<int:crew_id>/generate_profile_link')
@login_required
def generate_profile_link(crew_id):
    """Generate private profile link for crew member"""
    crew_member = CrewMember.query.get_or_404(crew_id)
    token = crew_member.generate_profile_token()
    profile_url = url_for('crew_private_profile', crew_id=crew_id, token=token, _external=True)
    
    flash(f'Profile link generated: {profile_url}', 'success')
    return redirect(url_for('crew_profile', crew_id=crew_id))


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
