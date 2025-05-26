import os

SECRET_KEY = os.getenv("SECRET_KEY", "aabbccddeeffgghhiijjkkllmmnnoopp112233445566778899")
# SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://owow-admin:owow1@db:5432/owow_postgres_db")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://owow-admin:owow1@192.168.7.207:5432/owow_postgres_db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")
# MONGO_URI = os.getenv("MONGO_URL", "mongodb://root:password@mongo:27017")
MONGO_URI = os.getenv("MONGO_URL", "mongodb://root:password@192.168.7.207:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB", "owow_mongo_db")