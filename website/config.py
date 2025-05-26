import os

SECRET_KEY = os.getenv("SECRET_KEY", "aabbccddeeffgghhiijjkkllmmnnoopp112233445566778899")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://owow-admin:owow1@db:5432/owow_postgres_db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")