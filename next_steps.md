# FormatHub: Project Next Steps & Roadmap
## Immediate Priorities
### 1. Optimize SQLite Large-File Hydration
The new SQLite processing backbone connects safely, but large production databases with millions of rows will crash the `ConversionService` when executing the `pd.read_sql_query` instruction.
* Refactor the connector to utilize `fetchmany()` limits and pagination to protect the server's cache size constraints.
* Allow users to query and select specific tables from SQLite databases upon upload, instead of merely defaulting to the *first* detected table.

### 2. Background Task Execution
FormatHub requires an asynchronous job message queue. Splitting a huge data block freezes the HTTP process.
* Map critical routes (`/split`, `/merge`, `/convert`) against a `Celery` worker queue.
* Implement a persistent Websocket / Polling architecture on `dashboard.html` to alert the user dynamically when the UI can refresh with the newly generated background payload without reloading the screen.

### 3. Broaden Format Integrations
With Pandas securely integrated, FormatHub should support:
* **Parquet:** High density binary data stores extensively requested in Big Data engineering.
* **JSON:** Nesting/Unnesting NoSQL payloads uniformly into row/column formats mathematically.
* **Markdown Table Export:** Directly converting query snapshots into Github-flavored `.md` layouts natively.

## Long-Term Objectives
### 1. Direct Storage Mounts
FormatHub currently accepts direct local multi-part file uploads and stores via Cloudinary BLOB.
* Build native OAuth integrations with AWS S3, Google Drive, and Dropbox, enabling FormatHub to stream tabular edits directly into existing Enterprise Cloud Buckets natively.

### 2. Multi-User Collaboration Workspaces
The project currently manages an isolated Sandbox for each User via a primary key linkage inside `app.db`.
* Implement Organization grouping hierarchies so teams can selectively authorize shared access to raw data pipelines and conversions simultaneously without overlapping namespaces.
