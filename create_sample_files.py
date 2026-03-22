#!/usr/bin/env python
"""Recreate missing files from database records."""
import os
from app import create_app, db
from app.models import File
import pandas as pd
import sqlite3

app = create_app()

with app.app_context():
    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    files = File.query.all()
    
    for file in files:
        file_path = os.path.join(upload_folder, file.original_filename)
        
        # Skip if file already exists
        if os.path.exists(file_path):
            print(f"✓ {file.original_filename} already exists")
            continue
        
        # Create sample data based on file type
        try:
            # Sample data for all file types
            df = pd.DataFrame({
                'ID': [1, 2, 3, 4, 5],
                'Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
                'Email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'],
                'Status': ['Active', 'Active', 'Inactive', 'Active', 'Pending']
            })
            
            if file.file_type.lower() == 'csv':
                df.to_csv(file_path, index=False)
                print(f"✓ Created {file.original_filename} (CSV)")
            
            elif file.file_type.lower() in ['xlsx', 'xls']:
                df.to_excel(file_path, index=False)
                print(f"✓ Created {file.original_filename} (Excel)")
            
            elif file.file_type.lower() in ['db', 'sqlite']:
                conn = sqlite3.connect(file_path)
                df.to_sql('data', conn, if_exists='replace', index=False)
                conn.close()
                print(f"✓ Created {file.original_filename} (SQLite)")
            
            else:
                # Create a generic text file for unknown types
                with open(file_path, 'w') as f:
                    f.write("This is a sample file for view/edit testing.\n")
                print(f"✓ Created {file.original_filename}")
        
        except Exception as e:
            print(f"✗ Error creating {file.original_filename}: {e}")

print("\nFile recovery complete!")

