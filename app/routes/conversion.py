from flask import Blueprint, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from app.models import File, Conversion
from app import db
from app.services.conversion_service import ConversionService
import os
import logging
from app.routes.files import get_local_path

conversion_bp = Blueprint('conversion', __name__)

@conversion_bp.route('/convert/<int:file_id>/<target_format>')
@login_required
def convert(file_id, target_format):
    file = File.query.get_or_404(file_id)
    
    if file.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        input_path = get_local_path(file)
    except Exception as e:
        logging.exception(f"Error getting local path for file {file.id}")
        flash('Error fetching file for conversion.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    output_filename = f"converted_{file_id}.{target_format}"
    
    try:
        if target_format == 'xlsx':
            output_path = ConversionService.convert_to_excel(input_path, output_filename)
        elif target_format == 'csv':
            output_path = ConversionService.convert_to_csv(input_path, output_filename)
        elif target_format == 'txt':
            output_path = ConversionService.convert_to_txt(input_path, output_filename)
        elif target_format == 'pdf':
            output_path = ConversionService.convert_to_pdf(input_path, output_filename)
        elif target_format in ['db', 'sqlite']:
            output_path = ConversionService.convert_to_sqlite(input_path, output_filename)
        elif target_format == 'sql':
            output_path = ConversionService.convert_to_sql(input_path, output_filename)
        else:
            flash(f'Conversion from {file.file_type} to {target_format} not supported yet.', 'warning')
            return redirect(url_for('dashboard.index'))
        
        # Upload converted file to Cloudinary
        from app.services.cloudinary_service import CloudinaryService
        try:
            cloudinary_url, public_id = CloudinaryService.upload_file(output_path, folder=f"user_{current_user.id}/converted")
            
            new_conversion = Conversion(
                file_id=file.id,
                output_format=target_format,
                cloudinary_url=cloudinary_url,
                public_id=public_id
            )
            db.session.add(new_conversion)
            db.session.commit()
            
            if os.path.exists(output_path):
                os.remove(output_path)
            
            flash(f'File converted to {target_format} successfully and saved to Cloud!', 'success')
        except Exception as e:
            logging.exception("Error uploading conversion to Cloudinary")
            flash(f'Error uploading conversion to Cloudinary: {str(e)}', 'danger')
            # Fallback to local if needed, but for now we error
            
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        logging.exception("Error during file conversion")
        flash(f'Error during conversion: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))

@conversion_bp.route('/download/<int:conversion_id>')
@login_required
def download(conversion_id):
    conversion = Conversion.query.get_or_404(conversion_id)
    file = File.query.get(conversion.file_id)
    
    if file.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if conversion.cloudinary_url:
        return redirect(conversion.cloudinary_url)
    
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], conversion.public_id, as_attachment=True)
