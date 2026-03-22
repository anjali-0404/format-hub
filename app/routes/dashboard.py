from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import File
from app import db
import os
from werkzeug.utils import secure_filename

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    files = File.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', files=files)

@dashboard_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Upload to Cloudinary
        from app.services.cloudinary_service import CloudinaryService
        try:
            cloudinary_url, public_id = CloudinaryService.upload_file(file_path, folder=f"user_{current_user.id}/originals")
            
            new_file = File(
                user_id=current_user.id,
                original_filename=filename,
                cloudinary_url=cloudinary_url,
                public_id=public_id,
                file_type=filename.split('.')[-1] if '.' in filename else 'unknown'
            )
            db.session.add(new_file)
            db.session.commit()
            flash('File uploaded successfully!', 'success')
        except Exception as e:
            import logging
            logging.exception("Error uploading to Cloudinary")
            flash(f'Error uploading to Cloudinary: {str(e)}', 'danger')
        finally:
            # Only remove local file if cloud upload succeeded
            if cloudinary_url and os.path.exists(file_path):
                os.remove(file_path)
        
        return redirect(url_for('dashboard.index'))
