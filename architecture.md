# FormatHub: System Architecture

The overarching architecture of FormatHub leverages a classic 3-Tier model utilizing **Flask (Python)** as the application engine, heavily supercharged by the **Pandas** dataframe ecosystem.

## 1. Frontend Client Layer
The UI is a server-side rendered suite of HTML templates leveraging **Jinja2** inside Flask.
* **Bootstrap 5.3:** Manages component structure (Modals, Buttons, Alerts, and Grids) to enforce a clean, enterprise-grade look out-of-the-box.
* **DataTables.js & jQuery:** Hydrates static HTML tables when viewing a file, enabling fast client-side sorting, pagination, and data-entry editing workflows. Interactive edits are batched as a JSON payload and handed off explicitly to the backend API via Fetch/AJAX.

## 2. Server Application Layer (Flask)
The business logic tier is composed of explicitly separated route blueprints and services to avoid spaghetti code.
* **`app/routes/auth.py`:** Manages robust user sessions via `Flask-Login` combined with `Werkzeug` secure password hashing.
* **`app/routes/dashboard.py`:** Defines the main hub, querying user-specific blob mappings from the internal meta-database.
* **`app/routes/files.py`:** Houses the heavyweight operations. Includes complex Pythonic manipulation to support merging array blobs and partitioning data chunks using mathematical logic. Serves as the primary bridge to the SQLite/Pandas data engines.
* **`app/routes/conversion.py`:** Acts as the traffic controller, catching the target output formats and delegating them to the stateless `ConversionService`.

## 3. Data Processing Engine (Pandas / sqlite3)
Data parsing is strictly relegated to the **Pandas** analytics framework and the built-in **sqlite3** library.
1. When a `.csv`, `.xlsx`, or `.db` file comes through the pipeline, the `ConversionService._read_file()` helper automatically identifies its structure natively. 
2. It generates a purely in-memory Pandas `DataFrame`.
3. Mutations, splits, appends, and queries act safely against the resilient `DataFrame` structure.
4. Finally, the framework writes the output back to disk natively via `.to_csv()`, `.to_excel()`, or `.to_sql()`.

## 4. Storage & Persistence Contexts
The application explicitly separates temporary binary payload states from long-term user metadata persistence.
* **Internal State Database (`app.db` via SQLAlchemy):** Uses SQLite to maintain light-weight maps of User credentials (`models.User`) and file linkage matrices (`models.File`, `models.Conversion`). This never holds actual user data payloads.
* **External BLOB Storage (Cloudinary API):** Physical file datastores (Spreadsheets, DBs) are pushed out via an external secure HTTP POST to Cloudinary. The application retrieves only lightweight metadata handles (`cloudinary_url`).
* **Ephemeral Local Cache (`/uploads`):** Handled aggressively within Python `finally` blocks, local cache states exist only for milliseconds while a dataframe is serialized for upload to Cloudinary. This guarantees FormatHub suffers from 0 persistent disk-bloat.
