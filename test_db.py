import os
import pymysql
from urllib.parse import urlparse
from app.config import settings

def test_connection():
    print("=" * 60)
    print("ShopSense - MySQL Connection Diagnostic")
    print("=" * 60)
    print(f"Configured DATABASE_URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")

    parsed = urlparse(settings.DATABASE_URL)
    from urllib.parse import unquote_plus
    user = unquote_plus(parsed.username) if parsed.username else "root"
    password = unquote_plus(parsed.password) if parsed.password else ""
    host = parsed.hostname or "localhost"
    port = parsed.port or 3306
    db_name = parsed.path.lstrip("/")

    print(f"Connecting to Host: {host}, Port: {port}, User: {user}...")

    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        print(" Connected to MySQL Server successfully!")

        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
            print(f"MySQL Version: {version[0]}")

            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f" Database '{db_name}' verified/created.")

        conn.close()
        print("\nAll database pre-flight checks passed!")
        print("You can now run:")
        print("  python create_tables.py")
        print("  python seed_data.py")
        print("=" * 60)
        return True
    except pymysql.err.OperationalError as e:
        print(f"\n MySQL Connection Failed:")
        print(f"Error Code: {e.args[0]}")
        print(f"Details: {e.args[1]}")
        if e.args[0] == 1045:
            print("\n TIP: Access denied for root user.")
            print("Please update the password in your .env file:")
            print("DATABASE_URL=mysql+pymysql://root:YOUR_ACTUAL_PASSWORD@localhost:3306/shopsense")
        print("=" * 60)
        return False

if __name__ == "__main__":
    test_connection()
