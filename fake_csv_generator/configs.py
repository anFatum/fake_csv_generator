import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv())
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", False)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(',')

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_PORT = os.getenv("REDIS_PORT")


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
