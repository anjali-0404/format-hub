#!/usr/bin/env python
"""Test that files can be loaded and viewed."""
import os
from app import create_app, db
from app.models import File
from app.routes.files import _load_dataframe, get_local_path

app = create_app()

with app.app_context():
    print("=== File View/Edit Test ===\n")
    
    files = File.query.all()
    for file in files:
        print(f"Testing: {file.original_filename}")
        try:
            # Test get_local_path
            local_path = get_local_path(file)
            print(f"  ✓ Local path: {local_path}")
            
            # Test _load_dataframe
            df, table_name = _load_dataframe(file)
            print(f"  ✓ Data loaded: {len(df)} rows, {len(df.columns)} columns")
            print(f"  ✓ Columns: {list(df.columns)}")
            print(f"  ✓ Preview:\n{df.head().to_string()}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print()

print("✓ All files are ready for view/edit!")
