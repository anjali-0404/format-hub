# 🧾 Project: FormatHub

## 📌 Overview

A full-stack web application that enables authenticated users to:

* Upload data files (CSV, Excel, SQLite)
* Convert files into multiple formats (CSV, Excel, SQLite, TXT, PDF)
* Store and retrieve files securely via cloud storage
* View and edit tabular data through a web interface
* Manage all files through a personalized dashboard

---

# 🏗️ System Architecture

## 1. Backend (Flask)

The backend is built using **Flask** and follows a modular architecture:

### Core Responsibilities:

* Authentication & session management
* File upload and validation
* Data processing and conversion
* Integration with cloud storage (Cloudinary)
* RESTful API endpoints
* Database interaction (SQLite via ORM)

---

## 2. Frontend

Server-rendered UI using:

* Jinja2 templates
* Bootstrap (for responsive UI)

### Key Views:

* Authentication pages (login/register)
* User dashboard
* File upload interface
* File conversion panel
* Data viewer/editor

---

## 3. Database Layer (SQLite)

SQLite is used for lightweight persistence during development and MVP stage.

### ORM:

* Flask-SQLAlchemy

### Schema Design:

#### Users Table

```
id (PK)
username (unique)
email (unique)
password_hash
created_at
```

#### Files Table

```
id (PK)
user_id (FK → Users.id)
original_filename
cloudinary_url
public_id (Cloudinary reference)
file_type
created_at
```

#### Conversions Table

```
id (PK)
file_id (FK → Files.id)
output_format
cloudinary_url
public_id
created_at
```

---

# 🔐 Authentication System

Implemented using:

* Flask-Login
* Werkzeug security utilities

### Features:

* User registration with hashed passwords
* Login/logout functionality
* Session persistence
* Route protection via `@login_required`

---

# 📁 File Storage (Cloudinary Integration)

Cloud storage is handled via:

* Cloudinary

### Storage Strategy:

* Each uploaded file is stored with a unique `public_id`
* Files are organized logically using folder prefixes:

  ```
  user_{id}/original/
  user_{id}/converted/
  ```

### Metadata stored in DB:

* `cloudinary_url`
* `public_id`

### Benefits:

* Eliminates need for local storage in production
* Enables secure file access and delivery
* Scales automatically

---

# 🔄 File Processing & Conversion Engine

## Core Library:

* pandas

## Supported Input Formats:

* CSV
* Excel (.xlsx)
* SQLite (.db)

## Supported Output Formats:

* CSV
* Excel
* SQLite
* TXT
* PDF

---

## Conversion Workflow:

1. Download file temporarily from Cloudinary
2. Load into pandas DataFrame
3. Apply transformation based on requested format
4. Save converted file locally (temporary)
5. Upload converted file to Cloudinary
6. Store metadata in Conversions table
7. Remove temporary file

---

## Format Handling:

### CSV / Excel:

* `pandas.read_csv()`
* `pandas.read_excel()`

### SQLite:

* `sqlite3.connect()`
* `pandas.read_sql()`

### TXT:

* `DataFrame.to_csv(sep="\t")`

### PDF:

* HTML rendering + PDF generation (WeasyPrint)

---

# 📊 Data Viewer & Editor

## Viewing:

* DataFrames rendered as HTML tables:

  ```python
  df.to_html()
  ```

## Editing:

Two approaches:

### Basic:

* Editable HTML form submission

### Advanced (recommended):

* DataTables.js or similar JS grid
* AJAX-based updates to backend

### Update Flow:

1. User edits data in UI
2. Changes sent via POST request
3. Backend updates DataFrame
4. File re-saved and re-uploaded

---

# 📡 API Design

## Authentication

```
POST /register
POST /login
GET  /logout
```

## File Management

```
POST /upload
GET  /files
GET  /download/<file_id>
```

## Conversion

```
POST /convert/<file_id>
GET  /conversions/<file_id>
```

## Data Interaction

```
GET  /view/<file_id>
POST /edit/<file_id>
```

---

# 📂 Project Structure

```
project/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── files.py
│   │   └── conversion.py
│   │
│   ├── services/
│   │   ├── cloudinary_service.py
│   │   ├── conversion_service.py
│   │
│   ├── utils/
│   │   └── file_utils.py
│
├── templates/
├── static/
├── config.py
├── run.py
```

---

# ⚙️ Configuration

### Environment Variables:

```
SECRET_KEY
DATABASE_URL
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
```

---

# 🚀 Deployment Strategy

## Backend Hosting:

* Render or Railway

## Database:

* SQLite (initial)
* Upgrade to PostgreSQL in production

## File Storage:

* Cloudinary (fully managed)

---

# 🔒 Security Considerations

* Validate file types before processing
* Limit upload size
* Use `secure_filename`
* Authenticate all file access routes
* Avoid exposing raw Cloudinary public IDs
* Use signed URLs for sensitive downloads

---

# 📈 Future Enhancements

* Background job queue (Celery + Redis)
* File versioning
* Multi-file batch conversion
* User quotas
* Sharing/export links
* React frontend (SPA)

---

# 🧪 Development Phases

### Phase 1 (MVP)

* Auth system
* File upload
* CSV ↔ Excel conversion
* Dashboard UI

### Phase 2

* Cloudinary integration
* All format conversions
* File download system

### Phase 3

* Data editor
* UI improvements
* Performance optimization
