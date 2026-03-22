import pandas as pd
import os
from flask import current_app

class ConversionService:
    @classmethod
    def _read_file(cls, input_path):
        import sqlite3
        if input_path.endswith('.csv'):
            return pd.read_csv(input_path)
        elif input_path.endswith('.xlsx') or input_path.endswith('.xls'):
            return pd.read_excel(input_path)
        elif input_path.endswith('.db') or input_path.endswith('.sqlite'):
            conn = sqlite3.connect(input_path)
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
            tname = tables.iloc[0]['name'] if not tables.empty else 'data'
            df = pd.read_sql_query(f"SELECT * FROM {tname}", conn)
            conn.close()
            return df
        elif input_path.endswith('.sql'):
            try:
                conn = sqlite3.connect(input_path)
                tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
                if not tables.empty:
                    tname = tables.iloc[0]['name']
                    df = pd.read_sql_query(f"SELECT * FROM {tname}", conn)
                    conn.close()
                    return df
                conn.close()
            except Exception:
                pass

            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                script = f.read()
            conn = sqlite3.connect(':memory:')
            conn.executescript(script)
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
            if tables.empty:
                conn.close()
                return pd.DataFrame()
            tname = tables.iloc[0]['name']
            df = pd.read_sql_query(f"SELECT * FROM {tname}", conn)
            conn.close()
            return df
        return pd.DataFrame()

    @classmethod
    def convert_to_excel(cls, input_path, output_filename):
        df = cls._read_file(input_path)
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
        df.to_excel(output_path, index=False)
        return output_path

    @classmethod
    def convert_to_csv(cls, input_path, output_filename):
        df = cls._read_file(input_path)
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
        df.to_csv(output_path, index=False)
        return output_path

    @classmethod
    def convert_to_txt(cls, input_path, output_filename):
        df = cls._read_file(input_path)
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
        df.to_csv(output_path, sep='\t', index=False)
        return output_path

    @classmethod
    def convert_to_pdf(cls, input_path, output_filename):
        df = cls._read_file(input_path)
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
        html = df.to_html(classes='table table-striped')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"<html><body>{html}</body></html>")
        return output_path

    @classmethod
    def convert_to_sqlite(cls, input_path, output_filename):
        import sqlite3
        df = cls._read_file(input_path)
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
        conn = sqlite3.connect(output_path)
        df.to_sql('data', conn, index=False, if_exists='replace')
        conn.close()
        return output_path

    @classmethod
    def convert_to_sql(cls, input_path, output_filename):
        import sqlite3
        df = cls._read_file(input_path)
        output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)

        conn = sqlite3.connect(':memory:')
        df.to_sql('data', conn, index=False, if_exists='replace')

        with open(output_path, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        conn.close()
        return output_path

