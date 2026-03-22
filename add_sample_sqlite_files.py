#!/usr/bin/env python
"""Add sample SQLite files to database for testing merge/split/view operations."""
import os
import sqlite3
import pandas as pd
from app import create_app, db
from app.models import File, User

app = create_app()

with app.app_context():
    # Get or create test user (assuming first user exists from previous test)
    user = User.query.first()
    if not user:
        # User.query.first() requires a user to exist; skip if none exists
        print("No users found. Please register/login first to test.")
        exit(1)
    
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    # Sample data for SQLite files - same schema for merge testing
    df1 = pd.DataFrame({
        'ID': [1, 2, 3],
        'Name': ['Product A', 'Product B', 'Product C'],
        'Email': ['info@a.com', 'info@b.com', 'info@c.com'],
        'Status': ['Available', 'Available', 'Unavailable']
    })
    
    df2 = pd.DataFrame({
        'ID': [4, 5, 6],
        'Name': ['Product D', 'Product E', 'Product F'],
        'Email': ['info@d.com', 'info@e.com', 'info@f.com'],
        'Status': ['Available', 'Unavailable', 'Available']
    })
    
    # Create SQLite files
    files_to_create = [
        ('sample_db_1.db', df1, 'SQLite sample 1'),
        ('sample_db_2.db', df2, 'SQLite sample 2'),
    ]
    
    for filename, data, description in files_to_create:
        file_path = os.path.join(upload_folder, filename)
        
        # Check if file already exists in database
        existing = File.query.filter_by(
            user_id=user.id,
            original_filename=filename
        ).first()
        
        if existing:
            print(f"✓ {filename} already in database")
            continue
        
        try:
            # Create SQLite file
            conn = sqlite3.connect(file_path)
            data.to_sql('data', conn, if_exists='replace', index=False)
            conn.close()
            
            # Add to database (without Cloudinary, local file only)
            new_file = File(
                user_id=user.id,
                original_filename=filename,
                cloudinary_url=None,
                public_id=None,
                file_type='db'
            )
            db.session.add(new_file)
            db.session.commit()
            
            print(f"✓ Created {filename} - {description}")
            
        except Exception as e:
            print(f"✗ Error creating {filename}: {e}")
    
    print("\nSQLite sample files added successfully!")
    print("You can now:")
    print("  1. View each SQLite file (File > View/Edit)")
    print("  2. Merge multiple SQLite files (select 2+ files > Merge Selected)")
    print("  3. View merged SQLite files")
    print("  4. Split SQLite files into smaller chunks or row ranges")
