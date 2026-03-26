# FormatHub - Enhanced Features Guide
## ✅ What's New

### 1. SQLite Database Support

- **Create** new SQLite database files (.db) directly in the app
- **View/Edit** data in SQLite databases in table format
- **Merge** multiple SQLite files with same schema
- **Split** SQLite files by chunk size or row range
- **Convert** between CSV, Excel, and SQLite formats

### 2. Enhanced File Creation

When creating a new file, you can now choose:

- **CSV** - Spreadsheet format (comma-separated values)
- **Excel** - XLSX format (Microsoft Excel)
- **SQLite** - Database format (.db files)

### 3. Smart Merge Operations

- ✅ **Same file type required** - Can't mix CSV with SQLite, etc.
- ✅ **Same schema required** - All files must have identical columns
- ✅ **Viewable merged files** - Merged files appear in dashboard and can be viewed immediately
- ✅ **Type validation** - If files are incompatible, merge button is disabled with clear error message

### 4. Improved File Operations

- ✅ **View** - Display file contents in interactive table format
- ✅ **Edit** - Click cells to edit data inline
- ✅ **Local fallback** - Files work even without cloud storage
- ✅ **Schema validation** - Automatic checking for merge compatibility

---

## 🚀 How to Use

### Starting the Application

```bash
cd D:\format-hub-main
d:.venv\Scripts\python.exe run.py
```

Then open: `http://127.0.0.1:4000`

### Creating a New File

1. Click **"Create New"** button
2. Enter filename (without extension)
3. Choose file type: CSV / Excel / SQLite
4. Click **"Create File"**
5. New file appears in dashboard ready to edit

### Merging Files

1. Select 2 or more files of the **same type**
2. Files must have **identical columns** (schema)
3. Click **"Merge Selected"** button
4. Merged file created automatically
5. View merged results immediately

### Viewing/Editing Files

1. Click **"View/Edit"** button on any file
2. See data in table format
3. Click any cell to edit data
4. Save changes (auto-saves to both local and cloud)

### Splitting Files

1. Click **"Split"** button
2. Choose split method:
   - **By Chunk Size**: Split into equal parts (e.g., 100 rows per file)
   - **Custom Range**: Extract specific row range (e.g., rows 5-20)
3. New files created automatically

### Converting Files

Click any conversion button (CSV, Excel, PDF, DB, SQL) to convert file format

---

## 📊 Sample Data

The app comes with sample files:

- **my_data.csv** - Sample CSV file with 5 records
- **sample_db_1.db** - Sample SQLite database (3 products)
- **sample_db_2.db** - Sample SQLite database (3 products)
- **my_data_part1.csv**, **my_data_part2.csv**, **my_data_part3.csv** - Split examples

Try:

1. **Viewing**: Click "View/Edit" on sample_db_1.db to see SQLite data
2. **Merging**: Select sample_db_1.db + sample_db_2.db → "Merge Selected" → View merged results
3. **Splitting**: Click "Split" on my_data.csv → Choose chunk size (e.g., 2 rows)

---

## ✨ Key Features

### File Type Support

- ✅ CSV (Comma-separated values)
- ✅ Excel (.xlsx, .xls)
- ✅ SQLite Database (.db)
- ✅ SQL Dumps (.sql)
- ✅ Conversions to: PDF, TXT, and more

### Validation & Safety

- ✅ Schema validation for merging
- ✅ File type consistency checking
- ✅ Local file fallback (works without cloud storage)
- ✅ Automatic error messages

### User Experience

- ✅ Intuitive dashboard interface
- ✅ Real-time merge button state (grayed out if incompatible)
- ✅ Interactive table editing
- ✅ Progress feedback with flash messages
- ✅ Mobile-responsive design

---

## 🔧 Technical Details

### File Organization

- **Local Storage**: `/uploads` folder (automatically created)
- **Cloud Storage**: Cloudinary (optional backup)
- **Database**: SQLite app.db (user accounts and file metadata)

### Supported Operations

| Operation | CSV | Excel | SQLite |
| --------- | --- | ----- | ------ |
| View/Edit | ✓   | ✓     | ✓      |
| Create    | ✓   | ✓     | ✓      |
| Merge     | ✓   | ✓     | ✓      |
| Split     | ✓   | ✓     | ✓      |
| Convert   | ✓   | ✓     | ✓      |

### Merge Rules

- Files must be **same type** (can't merge CSV + SQLite)
- Files must have **identical columns** in same order
- Row counts can be different
- Merged file inherits original file type

---

## 📝 Example Workflows

### Workflow 1: Working with SQLite

```
1. Create New File → Select "SQLite Database" → "my_products.db"
2. View/Edit → Add product data
3. Create another SQLite file "more_products.db"
4. Merge both files → View merged database
5. Split merged file by 5 rows per chunk
```

### Workflow 2: Data Consolidation

```
1. Upload multiple CSV files (same structure)
2. Select all CSV files
3. Click "Merge Selected"
4. Convert merged file to Excel for report
5. Download as .xlsx
```

### Workflow 3: Data Analysis

```
1. Create new SQLite database
2. View/Edit to populate sample data
3. Split by row range (extract top 10 rows)
4. Convert to CSV for Excel analysis
5. Convert to PDF for sharing
```

---

## ⚠️ Common Issues & Solutions

### "Files incompatible for merge"

- **Cause**: Different column names or order
- **Solution**: Files must have identical columns in same order

### "Merge button is disabled"

- **Cause**: Selected files are different types or incompatible
- **Solution**: Select only files of same type with same schema

### "Cannot view file"

- **Cause**: File missing from uploads folder (cloud-only backup)
- **Solution**: Re-upload file or ensure Cloudinary is configured

### "Merged file not appearing"

- **Cause**: Page needs refresh
- **Solution**: Click browser refresh or restart browser tab

---

## 🎯 Best Practices

1. **Keep consistent schemas** - Use same column names across files to merge
2. **Use SQLite for large datasets** - Better for complex queries than CSV
3. **Backup important files** - Download converted copies (PDF, Excel)
4. **Test with samples first** - Use sample files to understand features
5. **Check merge compatibility** - Button will show if files can merge

---

**Version**: Enhanced SQLite Support
**Last Updated**: March 22, 2026
