import sys
from app.database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        cols = [c[0] for c in conn.execute(text("DESCRIBE users")).fetchall()]
        print("Current columns in users:", cols)
        if "phone" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(30) NULL;"))
            conn.commit()
            print("Successfully added phone column to users table.")
        else:
            print("Phone column already present in users table.")
        
        # Check General category
        cat_exists = conn.execute(text("SELECT category_id FROM categories WHERE category_name = 'General'")).fetchone()
        if not cat_exists:
            conn.execute(text("INSERT INTO categories (category_name, parent_category) VALUES ('General', NULL);"))
            conn.commit()
            print("Successfully added General category to categories table.")
        else:
            print("General category already present in categories table.")

if __name__ == "__main__":
    run_migration()
