# FormatHub: Project Overview

## What is FormatHub?
FormatHub is an advanced, lightweight web-based file manipulation and conversion utility. Targeted towards data workers and developers, it centralizes the core capabilities of spreadsheet manipulation into an agile online dashboard. Without needing complex local software like Excel or SQL clients, users can upload raw datasets and universally manipulate them natively in the browser.

## Core Purpose
The fundamental objective of FormatHub is to solve the bottleneck of format lock-in. Developers often hold data in SQLite databases (`.db`, `.sqlite`) while business departments require cleanly formatted `.xlsx` or `.csv` sheets, or even `.pdf` printouts. Rather than writing custom scripts to ferry this data around, FormatHub functions as a drag-and-drop translator between these silos while retaining native editing capability.

## Key Capabilities

### 1. Omni-directional Data Conversion
The platform handles secure data format transformations spanning complex tables and sheets. 
* Converts raw datastores (`.db`, `.sqlite`) gracefully into standard `.csv` or `.xlsx` files.
* Allows compiling flat files (`.csv`, `.xlsx`) dynamically into robust `.sqlite` databanks or visual `.pdf` and textual `.txt` printouts.
* Fully extensible architecture ensures further formats (like JSON or Parquet) can be slotted natively into the pipeline.

### 2. Browser-Native Data Editor
Users can view and edit tabular data directly in their dashboard without a round-trip download. 
* Powered by `DataTables.js`, enormous data chunks are hydrated intuitively.
* Native DOM-level Add (`+`) and Delete (`-`) icons allow offline-style drafting of changes to datasets.
* A single "Save Changes" bulk-uploader ensures network traffic is completely minimized by reconstructing the data into an array and committing it to the server in a single reliable HTTP Post packet.

### 3. File Splitting and Merging
Large data dumps are easily broken apart or stitched together.
* **Splitting:** Easily shard a 5,000-row file into 10 smaller parts by Chunk Size, or explicitly slice out rows using the Custom Range modal.
* **Merging:** Utilizing dashboard checkboxes, multiple CSV or SQLite files can be immediately aggregated into a unified master file.

### 4. Headless Cloud Uploading
All data files are treated ephemerally on the application server. Files are streamed locally only for computational data analysis via Pandas, and permanently flushed to secure external **Cloudinary** blob buckets immediately thereafter, keeping the application exceptionally lightweight.
