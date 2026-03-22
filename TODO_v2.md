# TODO: Add SQLite/SQL Merge/Split Schema Validation

## Steps:

- [x] Step 1: Add /check_merge_compat endpoint in app/routes/files.py (check selected files have same schema for sqlite/sql).
- [x] Step 2: Update templates/dashboard.html (JS AJAX to endpoint, disable/enable merge button based on compat).
- [x] Step 3: Add server-side schema validation in merge_files(). (Split is single-file, no multi-schema check needed.)
- [ ] Step 4: Test with sample sqlite files.

Current progress: Step 1 complete (read dashboard.html).
