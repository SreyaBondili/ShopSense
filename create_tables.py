import os
import pymysql
from urllib.parse import urlparse
from app.config import settings
from app.database import engine, Base
from app.models import User, Vendor, Product, Inventory, Transaction

def ensure_database_exists(db_url: str):
    """If using MySQL, ensure the target database schema exists."""
    if "mysql" in db_url:
        from urllib.parse import unquote_plus
        parsed = urlparse(db_url)
        db_name = parsed.path.lstrip("/")
        user = unquote_plus(parsed.username) if parsed.username else "root"
        password = unquote_plus(parsed.password) if parsed.password else ""
        host = parsed.hostname or "localhost"
        port = parsed.port or 3306

        print(f"Connecting to MySQL server at {host}:{port} to verify database '{db_name}'...")
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            print(f"Database '{db_name}' ensured successfully.")
        finally:
            conn.close()

def create_all_tables():
    print(f"Using DATABASE_URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    ensure_database_exists(settings.DATABASE_URL)
    print("Creating tables in database...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    create_all_tables()
