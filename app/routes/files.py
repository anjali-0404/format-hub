from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.models import File
from app import db
import os
import pandas as pd
import sqlite3
from werkzeug.utils import secure_filename

files_bp = Blueprint('files', __name__)

SQLITE_TYPES = {'db', 'sqlite', 'sql'}


def _read_sqlite_like(path):
    # Supports both SQLite binary files and SQL script dumps.
    try:
        conn = sqlite3.connect(path)
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
        if not tables.empty:
            tname = tables.iloc[0]['name']
            df = pd.read_sql_query(f"SELECT * FROM {tname}", conn)
            conn.close()
            return df, tname
        conn.close()
    except Exception:
        pass

    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        script = f.read()

    conn = sqlite3.connect(':memory:')
    conn.executescript(script)
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
    if tables.empty:
        conn.close()
        return pd.DataFrame(columns=['Column1']), 'data'
    tname = tables.iloc[0]['name']
    df = pd.read_sql_query(f"SELECT * FROM {tname}", conn)
    conn.close()
    return df, tname


def _load_dataframe(file):
    local_path = get_local_path(file)
    ftype = file.file_type.lower()
    if ftype == 'csv':
        return pd.read_csv(local_path), None
    if ftype in ['xlsx', 'xls']:
        return pd.read_excel(local_path), None
    if ftype in SQLITE_TYPES:
        return _read_sqlite_like(local_path)
    raise ValueError(f'Unsupported file type: {file.file_type}')


def _column_signature(df):
    return tuple(str(col).strip().lower() for col in df.columns)


def _write_sql_dump(df, output_path, table_name='data'):
    conn = sqlite3.connect(':memory:')
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    conn.close()

def get_local_path(file):
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)

    local_path = os.path.join(upload_dir, file.original_filename)
    safe_path = os.path.join(upload_dir, secure_filename(file.original_filename))

    if os.path.exists(local_path):
        return local_path
    if os.path.exists(safe_path):
        return safe_path

    if file.cloudinary_url:
        # Download from cloud storage if local copy is missing (e.g., after restart).
        import requests
        response = requests.get(file.cloudinary_url, timeout=30)
        response.raise_for_status()
        target_path = safe_path if safe_path != local_path else local_path
        with open(target_path, 'wb') as f:
            f.write(response.content)
        return target_path

    raise FileNotFoundError(
        f"File is not available locally and no cloud URL found for '{file.original_filename}'"
    )

@files_bp.route('/view/<int:file_id>')
@login_required
def view(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        try:
            df, _ = _load_dataframe(file)
        except ValueError:
            flash(f'Viewing this file type is not supported yet ({file.file_type}).', 'info')
            return redirect(url_for('dashboard.index'))
        
        df = df.fillna('')
        columns = df.columns.tolist()
        data = df.to_dict(orient='records')
        
        return render_template('view.html', file=file, columns=columns, data=data)
    except Exception as e:
        flash(f'Error loading file: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))

@files_bp.route('/insert_rows/<int:file_id>', methods=['POST'])
@login_required
def insert_rows(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    num_rows = request.json.get('num_rows', 1)
    position = request.json.get('position', 'end')  # 'beginning' or 'end'
    
    try:
        local_path = get_local_path(file)
        if file.file_type.lower() in SQLITE_TYPES:
            return jsonify({'error': 'Row insertion not supported for this file type'}), 400
        if file.file_type.lower() == 'csv':
            df = pd.read_csv(local_path)
        elif file.file_type.lower() in ['xlsx', 'xls']:
            df = pd.read_excel(local_path)
        else:
            return jsonify({'error': 'Row insertion not supported for this file type'}), 400
        
        # Create empty rows
        empty_rows = pd.DataFrame([['' for _ in df.columns]] * num_rows, columns=df.columns)
        
        if position == 'beginning':
            df = pd.concat([empty_rows, df], ignore_index=True)
        else:
            df = pd.concat([df, empty_rows], ignore_index=True)
        
        if file.file_type.lower() == 'csv':
            df.to_csv(local_path, index=False)
        else:
            df.to_excel(local_path, index=False)
        
        from app.services.cloudinary_service import CloudinaryService
        cloudinary_url, public_id = CloudinaryService.upload_file(local_path, folder=f"user_{current_user.id}/originals")
        if cloudinary_url:
            file.cloudinary_url = cloudinary_url
            file.public_id = public_id
        db.session.commit()
        
        return jsonify({'success': True, 'new_rows': num_rows})
    except Exception as e:
        import logging
        logging.exception("Error inserting rows")
        return jsonify({'error': str(e)}), 500


@files_bp.route('/save_all/<int:file_id>', methods=['POST'])
@login_required
def save_all(file_id):
    data = request.json
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format'}), 400

    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        df = pd.DataFrame(data)
        
        # Preserve original column names and order based on the file
        local_path = get_local_path(file)
        if file.file_type.lower() == 'csv':
             original_df = pd.read_csv(local_path)
             if list(df.columns) != list(original_df.columns):
                 df = df.reindex(columns=original_df.columns, fill_value='')
             df.to_csv(local_path, index=False)
        elif file.file_type.lower() in ['xlsx', 'xls']:
             original_df = pd.read_excel(local_path)
             if list(df.columns) != list(original_df.columns):
                 df = df.reindex(columns=original_df.columns, fill_value='')
             df.to_excel(local_path, index=False)
        elif file.file_type.lower() in SQLITE_TYPES:
             _, table_name = _load_dataframe(file)
             try:
                 original_df, _ = _load_dataframe(file)
                 if list(df.columns) != list(original_df.columns):
                     df = df.reindex(columns=original_df.columns, fill_value='')
             except Exception:
                 pass

             if file.file_type.lower() == 'sql':
                 _write_sql_dump(df, local_path, table_name=table_name or 'data')
             else:
                 conn = sqlite3.connect(local_path)
                 df.to_sql(table_name or 'data', conn, if_exists='replace', index=False)
                 conn.close()
            
        from app.services.cloudinary_service import CloudinaryService
        cloudinary_url, public_id = CloudinaryService.upload_file(local_path, folder=f"user_{current_user.id}/originals")
        if cloudinary_url:
            file.cloudinary_url = cloudinary_url
            file.public_id = public_id
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        import logging
        logging.exception("Error saving batch data")
        return jsonify({'error': str(e)}), 500

@files_bp.route('/new', methods=['POST'])
@login_required
def new_file():
    filename = request.form.get('filename', 'new_file').strip()
    file_type = request.form.get('file_type', 'csv').lower()
    
    if not filename:
        filename = 'new_file'
    
    # Validate file type
    valid_types = ['csv', 'xlsx', 'db']
    if file_type not in valid_types:
        file_type = 'csv'
    
    # Add proper extension
    if file_type == 'csv' and not filename.endswith('.csv'):
        filename += '.csv'
    elif file_type == 'xlsx' and not filename.endswith(('.xlsx', '.xls')):
        filename += '.xlsx'
    elif file_type == 'db' and not filename.endswith(('.db', '.sqlite')):
        filename += '.db'
    
    filename = secure_filename(filename)
    if not filename:
        filename = f'new_file.{file_type}'
        
    df = pd.DataFrame(columns=['Column1', 'Column2', 'Column3'])
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    try:
        if file_type == 'csv':
            df.to_csv(local_path, index=False)
        elif file_type == 'xlsx':
            df.to_excel(local_path, index=False)
        elif file_type == 'db':
            conn = sqlite3.connect(local_path)
            df.to_sql('data', conn, if_exists='replace', index=False)
            conn.close()
        
        from app.services.cloudinary_service import CloudinaryService
        cloudinary_url, public_id = CloudinaryService.upload_file(local_path, folder=f"user_{current_user.id}/originals")
        new_file = File(
            user_id=current_user.id,
            original_filename=filename,
            cloudinary_url=cloudinary_url,
            public_id=public_id,
            file_type=file_type
        )
        db.session.add(new_file)
        db.session.commit()
        # Only delete local file if cloud upload succeeded
        if cloudinary_url and os.path.exists(local_path):
            os.remove(local_path)
        flash('New file created successfully!', 'success')
    except Exception as e:
        import logging
        logging.exception("Error creating new file")
        flash(f'Error creating file: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard.index'))

@files_bp.route('/split/<int:file_id>', methods=['POST'])
@login_required
def split_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        try:
            df, table_name = _load_dataframe(file)
        except ValueError:
            flash(f'Splitting this file type is not supported yet ({file.file_type}).', 'info')
            return redirect(url_for('dashboard.index'))
            
        start_row = request.form.get('start_row')
        end_row = request.form.get('end_row')
        
        from app.services.cloudinary_service import CloudinaryService
        
        if start_row and end_row:
            # Custom range split
            s_idx = max(int(start_row) - 1, 0)
            e_idx = int(end_row)
            split_df = df.iloc[s_idx:e_idx]
            
            new_filename = f"{file.original_filename.rsplit('.', 1)[0]}_range_{int(start_row)}_{int(end_row)}.{file.file_type}"
            split_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
            
            if file.file_type.lower() == 'csv':
                split_df.to_csv(split_path, index=False)
            elif file.file_type.lower() in ['xlsx', 'xls']:
                split_df.to_excel(split_path, index=False)
            elif file.file_type.lower() in SQLITE_TYPES:
                if file.file_type.lower() == 'sql':
                    _write_sql_dump(split_df, split_path, table_name=table_name or 'data')
                else:
                    conn = sqlite3.connect(split_path)
                    split_df.to_sql(table_name or 'data', conn, if_exists='replace', index=False)
                    conn.close()
                
            cloudinary_url, public_id = CloudinaryService.upload_file(split_path, folder=f"user_{current_user.id}/originals")
            new_file = File(
                user_id=current_user.id,
                original_filename=new_filename,
                cloudinary_url=cloudinary_url,
                public_id=public_id,
                file_type=file.file_type
            )
            db.session.add(new_file)
            # Only delete local file if cloud upload succeeded
            if cloudinary_url and os.path.exists(split_path):
                os.remove(split_path)
                
            db.session.commit()
            flash('Custom range successfully extracted into a new file!', 'success')
            
        else:
            # Chunk size split
            rows_per_file = int(request.form.get('rows', 100))
            import math
            num_splits = math.ceil(len(df) / rows_per_file)
            if num_splits <= 1:
                flash('File is too small to split with the given row count.', 'info')
                return redirect(url_for('dashboard.index'))
                
            for i in range(num_splits):
                split_df = df.iloc[i*rows_per_file:(i+1)*rows_per_file]
                new_filename = f"{file.original_filename.rsplit('.', 1)[0]}_part{i+1}.{file.file_type}"
                split_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                
                if file.file_type.lower() == 'csv':
                    split_df.to_csv(split_path, index=False)
                elif file.file_type.lower() in ['xlsx', 'xls']:
                    split_df.to_excel(split_path, index=False)
                elif file.file_type.lower() in SQLITE_TYPES:
                    if file.file_type.lower() == 'sql':
                        _write_sql_dump(split_df, split_path, table_name=table_name or 'data')
                    else:
                        conn = sqlite3.connect(split_path)
                        split_df.to_sql(table_name or 'data', conn, if_exists='replace', index=False)
                        conn.close()
                    
                cloudinary_url, public_id = CloudinaryService.upload_file(split_path, folder=f"user_{current_user.id}/originals")
                new_file = File(
                    user_id=current_user.id,
                    original_filename=new_filename,
                    cloudinary_url=cloudinary_url,
                    public_id=public_id,
                    file_type=file.file_type
                )
                db.session.add(new_file)
                # Only delete local file if cloud upload succeeded
                if cloudinary_url and os.path.exists(split_path):
                    os.remove(split_path)
                    
            db.session.commit()
            flash(f'File successfully split into {num_splits} parts!', 'success')
    except Exception as e:
        import logging
        logging.exception("Error splitting file")
        flash(f'Error splitting file: {str(e)}', 'danger')
        
    return redirect(url_for('dashboard.index'))

@files_bp.route('/check_merge_compat', methods=['POST'])
@login_required
def check_merge_compat():
    file_ids = request.json.get('file_ids', [])
    if len(file_ids) < 2:
        return jsonify({'compatible': False, 'reason': 'Select at least 2 files'})
    
    files = File.query.filter(File.id.in_(file_ids), File.user_id == current_user.id).all()
    if len(files) != len(file_ids):
        return jsonify({'compatible': False, 'reason': 'Unauthorized or invalid files'})
    
    try:
        sig = None
        for file in files:
            df, _ = _load_dataframe(file)
            current_sig = _column_signature(df)
            if sig is None:
                sig = current_sig
            elif current_sig != sig:
                return jsonify({'compatible': False, 'reason': 'Selected files must have the same fields/columns'})
    except Exception as e:
        return jsonify({'compatible': False, 'reason': f'Cannot inspect selected files: {str(e)}'})

    return jsonify({'compatible': True, 'reason': ''})


@files_bp.route('/merge', methods=['POST'])
@login_required
def merge_files():
    file_ids = request.form.getlist('file_ids')
    if len(file_ids) < 2:
        flash('Please select at least 2 files to merge.', 'warning')
        return redirect(url_for('dashboard.index'))
        
    try:
        dfs = []
        base_type = None
        expected_signature = None
        
        for fid in file_ids:
            file = File.query.get(int(fid))
            if file and file.user_id == current_user.id:
                # Check file type consistency
                ftype = file.file_type.lower()
                if base_type is None:
                    base_type = 'sqlite' if ftype in SQLITE_TYPES else ('xlsx' if ftype in ['xlsx', 'xls'] else 'csv')
                else:
                    current_base = 'sqlite' if ftype in SQLITE_TYPES else ('xlsx' if ftype in ['xlsx', 'xls'] else 'csv')
                    if current_base != base_type:
                        flash('Cannot merge: all selected files must be the same type (CSV, Excel, or SQLite).', 'danger')
                        return redirect(url_for('dashboard.index'))
                
                # Load data and check schema consistency
                df, _ = _load_dataframe(file)
                current_sig = _column_signature(df)
                if expected_signature is None:
                    expected_signature = current_sig
                elif current_sig != expected_signature:
                    flash('Cannot merge: selected files must have the same fields/columns.', 'danger')
                    return redirect(url_for('dashboard.index'))
                dfs.append(df)
                    
        merged_df = pd.concat(dfs, ignore_index=True)
        if base_type is None:
            flash('No valid files selected for merge.', 'danger')
            return redirect(url_for('dashboard.index'))
        new_filename = f"merged_{len(file_ids)}_files.{base_type}"
        local_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
        
        if base_type == 'csv':
            merged_df.to_csv(local_path, index=False)
        elif base_type == 'xlsx':
            merged_df.to_excel(local_path, index=False)
        elif base_type == 'sqlite':
            if base_type == 'sql':
                _write_sql_dump(merged_df, local_path, table_name='data')
            else:
                conn = sqlite3.connect(local_path)
                merged_df.to_sql("data", conn, if_exists='replace', index=False)
                conn.close()
            
        from app.services.cloudinary_service import CloudinaryService
        cloudinary_url, public_id = CloudinaryService.upload_file(local_path, folder=f"user_{current_user.id}/originals")
        new_file = File(
            user_id=current_user.id,
            original_filename=new_filename,
            cloudinary_url=cloudinary_url,
            public_id=public_id,
            file_type=base_type
        )
        db.session.add(new_file)
        db.session.commit()
        # Only delete local file if cloud upload succeeded
        if cloudinary_url and os.path.exists(local_path):
            os.remove(local_path)
            
        flash(f'{len(file_ids)} files merged successfully! You can now view the merged file.', 'success')
    except Exception as e:
        import logging
        logging.exception("Error merging files")
        flash(f'Error merging files: {str(e)}', 'danger')
        
    return redirect(url_for('dashboard.index'))
