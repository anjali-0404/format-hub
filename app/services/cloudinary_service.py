import cloudinary
import cloudinary.uploader
from flask import current_app
import cloudinary.utils  # For potential future use

class CloudinaryService:
    @staticmethod
    def init_cloudinary():
        cloudinary.config(
            cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=current_app.config['CLOUDINARY_API_KEY'],
            api_secret=current_app.config['CLOUDINARY_API_SECRET']
        )

    @staticmethod
    def upload_file(file_path, folder='originals'):
        try:
            CloudinaryService.init_cloudinary()
            response = cloudinary.uploader.upload(file_path, folder=folder, resource_type="raw")
            return response['secure_url'], response['public_id']
        except (ValueError, KeyError) as e:
            if "api_key" in str(e):
                current_app.logger.warning(f"Cloudinary config missing: {e}. Using local storage only.")
                return None, None
            raise

    @staticmethod
    def upload_stream(file_stream, filename, folder='originals'):
        try:
            CloudinaryService.init_cloudinary()
            response = cloudinary.uploader.upload(file_stream, public_id=filename, folder=folder, resource_type="raw")
            return response['secure_url'], response['public_id']
        except (ValueError, KeyError) as e:
            if "api_key" in str(e):
                current_app.logger.warning(f"Cloudinary config missing: {e}. Using local storage only.")
                return None, None
            raise
