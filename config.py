import os
from dotenv import load_dotenv

load_dotenv()


def _is_vercel_runtime():
    return os.environ.get('VERCEL') == '1' or bool(os.environ.get('VERCEL_ENV'))


def _default_sqlite_uri():
    # Vercel's deployment filesystem is read-only; /tmp is writable at runtime.
    if _is_vercel_runtime():
        return 'sqlite:////tmp/app.db'
    return 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')


def _default_upload_folder():
    if _is_vercel_runtime():
        return '/tmp/uploads'
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or _default_sqlite_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or _default_upload_folder()
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
