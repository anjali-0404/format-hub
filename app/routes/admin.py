from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.models import User, File
from app import db
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator: user must be logged in AND have is_admin=True."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    files = File.query.order_by(File.created_at.desc()).all()
    return render_template('admin.html', users=users, files=files)


@admin_bp.route('/upload', methods=['POST'])
@login_required
@admin_required
def upload():
    """Upload a file on behalf of any user."""
    target_user_id = request.form.get('target_user_id', type=int)
    if not target_user_id:
        flash('Please select a target user.', 'danger')
        return redirect(url_for('admin.index'))

    target_user = User.query.get_or_404(target_user_id)

    if 'file' not in request.files:
        flash('No file part.', 'danger')
        return redirect(url_for('admin.index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('admin.index'))

    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    from app.services.cloudinary_service import CloudinaryService
    try:
        cloudinary_url, public_id = CloudinaryService.upload_file(
            file_path, folder=f"user_{target_user.id}/originals"
        )
        new_file = File(
            user_id=target_user.id,
            original_filename=filename,
            cloudinary_url=cloudinary_url,
            public_id=public_id,
            file_type=filename.rsplit('.', 1)[-1] if '.' in filename else 'unknown'
        )
        db.session.add(new_file)
        db.session.commit()
        flash(f'File uploaded successfully for user "{target_user.username}".', 'success')
    except Exception as e:
        import logging
        logging.exception("Admin upload error")
        flash(f'Upload failed: {e}', 'danger')
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return redirect(url_for('admin.index'))


@admin_bp.route('/create/blank', methods=['POST'])
@login_required
@admin_required
def create_blank():
    """Create a blank CSV/Excel/DB file for the selected user."""
    target_user_id = request.form.get('target_user_id', type=int)
    file_format     = request.form.get('file_format', 'csv').lower()
    filename        = request.form.get('filename', 'new_file').strip()
    columns_raw     = request.form.get('columns', '').strip()

    if not target_user_id:
        flash('Please select a target user.', 'danger')
        return redirect(url_for('admin.index'))

    target_user = User.query.get_or_404(target_user_id)

    columns = [c.strip() for c in columns_raw.split(',') if c.strip()] if columns_raw else ['id', 'name', 'value']

    if not filename:
        filename = 'new_file'
    full_name = secure_filename(f"{filename}.{file_format}")
    local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], full_name)

    try:
        import pandas as pd
        df = pd.DataFrame(columns=columns)
        if file_format == 'csv':
            df.to_csv(local_path, index=False)
        elif file_format in ['xlsx', 'xls']:
            df.to_excel(local_path, index=False)
        elif file_format in ['db', 'sqlite']:
            import sqlite3
            conn = sqlite3.connect(local_path)
            df.to_sql('data', conn, if_exists='replace', index=False)
            conn.close()
        else:
            df.to_csv(local_path, index=False)
            full_name = secure_filename(f"{filename}.csv")

        from app.services.cloudinary_service import CloudinaryService
        cloudinary_url, public_id = CloudinaryService.upload_file(
            local_path, folder=f"user_{target_user.id}/originals"
        )
        new_file = File(
            user_id=target_user.id,
            original_filename=full_name,
            cloudinary_url=cloudinary_url,
            public_id=public_id,
            file_type=file_format
        )
        db.session.add(new_file)
        db.session.commit()
        flash(f'Blank {file_format.upper()} file "{full_name}" created for user "{target_user.username}".', 'success')
    except Exception as e:
        import logging
        logging.exception("Admin create_blank error")
        flash(f'Error creating file: {e}', 'danger')
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    return redirect(url_for('admin.index'))


# Pre-defined column templates
TEMPLATES = {
    'contacts': ['id', 'first_name', 'last_name', 'email', 'phone', 'company'],
    'orders':   ['order_id', 'customer_name', 'product', 'quantity', 'price', 'date'],
    'inventory':['item_id', 'name', 'sku', 'quantity', 'unit_price', 'location'],
    'employees':['emp_id', 'name', 'department', 'role', 'salary', 'hire_date'],
    'custom':   [],  # User provides their own columns
}

@admin_bp.route('/create/template', methods=['POST'])
@login_required
@admin_required
def create_from_template():
    """Create a file pre-filled with a column template."""
    target_user_id = request.form.get('target_user_id', type=int)
    template_key   = request.form.get('template', 'contacts')
    file_format    = request.form.get('file_format', 'csv').lower()
    filename       = request.form.get('filename', '').strip()
    custom_columns = request.form.get('custom_columns', '').strip()

    if not target_user_id:
        flash('Please select a target user.', 'danger')
        return redirect(url_for('admin.index'))

    target_user = User.query.get_or_404(target_user_id)
    columns = TEMPLATES.get(template_key, TEMPLATES['contacts'])

    if template_key == 'custom' and custom_columns:
        columns = [c.strip() for c in custom_columns.split(',') if c.strip()]

    if not columns:
        columns = ['id', 'value']

    if not filename:
        filename = f'{template_key}_template'

    full_name  = secure_filename(f"{filename}.{file_format}")
    local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], full_name)

    try:
        import pandas as pd
        df = pd.DataFrame(columns=columns)
        if file_format == 'csv':
            df.to_csv(local_path, index=False)
        elif file_format in ['xlsx', 'xls']:
            df.to_excel(local_path, index=False)
        elif file_format in ['db', 'sqlite']:
            import sqlite3
            conn = sqlite3.connect(local_path)
            df.to_sql('data', conn, if_exists='replace', index=False)
            conn.close()
        else:
            df.to_csv(local_path, index=False)

        from app.services.cloudinary_service import CloudinaryService
        cloudinary_url, public_id = CloudinaryService.upload_file(
            local_path, folder=f"user_{target_user.id}/originals"
        )
        new_file = File(
            user_id=target_user.id,
            original_filename=full_name,
            cloudinary_url=cloudinary_url,
            public_id=public_id,
            file_type=file_format
        )
        db.session.add(new_file)
        db.session.commit()
        flash(f'Template "{template_key}" file "{full_name}" created for user "{target_user.username}".', 'success')
    except Exception as e:
        import logging
        logging.exception("Admin create_from_template error")
        flash(f'Error creating template file: {e}', 'danger')
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    return redirect(url_for('admin.index'))
