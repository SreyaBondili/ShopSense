import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorStatus
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.transaction import Transaction
from app.utils.security import hash_password

def seed():
    db: Session = SessionLocal()
    try:
        print("Starting ShopSense database seeding...")

        # 1. Clear existing records to ensure fresh demo state
        print("Clearing old records...")
        from sqlalchemy import text
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.query(Transaction).delete()
        db.query(Inventory).delete()
        db.query(Product).delete()
        db.query(Vendor).delete()
        db.query(User).delete()
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        db.commit()

        # 2. Seed Users
        print("Seeding Users...")
        admin_user = User(
            full_name="Sreya Bondili (Admin)",
            email="bsreya1610@gmail.com",
            password_hash=hash_password("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        
        customer_user = User(
            full_name="Alice Johnson (Customer)",
            email="customer@shopsense.com",
            password_hash=hash_password("Customer@123"),
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db.add(customer_user)
        db.commit()
        db.refresh(admin_user)

        vendor_users_data = [
            ("Apex Electronics", "techworld@example.com", "John Doe", "Electronics", "9876543210"),
            ("Aura Fashion Hub", "trendsfashion@example.com", "Sarah Miller", "Fashion", "9876543211"),
            ("Book Haven Store", "bookoasis@example.com", "Robert Clark", "Books", "9876543212"),
            ("Urban Home Comforts", "homecomforts@example.com", "Emma Watson", "Home & Kitchen", "9876543213"),
            ("Glow Cosmetics & Spa", "glowbeauty@example.com", "Priya Sharma", "Beauty & Personal Care", "9876543214"),
        ]

        vendors = []
        for b_name, email, owner, cat, phone in vendor_users_data:
            v_user = User(
                full_name=owner,
                email=email,
                password_hash=hash_password("Vendor@123"),
                role=UserRole.VENDOR,
                is_active=True
            )
            db.add(v_user)
            db.commit()
            db.refresh(v_user)

            vendor = Vendor(
                business_name=b_name,
                owner_name=owner,
                email=email,
                phone=phone,
                category=cat,
                commission_rate=Decimal("12.50"),
                status=VendorStatus.ACTIVE,
                user_id=v_user.user_id
            )
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
            vendors.append(vendor)

        print(f"Created {len(vendors)} vendors with associated user accounts.")

        # 3. Seed Products (15 products: 3 per vendor)
        print("Seeding 15 Products and Inventory...")
        products_data = [
            # Vendor 1 - Apex Electronics
            ("Noise-Cancelling Wireless Headphones", "Electronics", Decimal("149.99"), 45, 12, vendors[0].vendor_id),
            ("Ultra-Slim Mechanical Keyboard", "Electronics", Decimal("89.50"), 30, 10, vendors[0].vendor_id),
            ("Smartwatch Pro Series 5", "Electronics", Decimal("199.00"), 25, 8, vendors[0].vendor_id),

            # Vendor 2 - Aura Fashion Hub
            ("Organic Cotton Graphic Tee", "Fashion", Decimal("29.99"), 80, 20, vendors[1].vendor_id),
            ("Classic Slim-Fit Denim Jeans", "Fashion", Decimal("59.95"), 50, 15, vendors[1].vendor_id),
            ("Lightweight Waterproof Windbreaker", "Fashion", Decimal("79.00"), 35, 10, vendors[1].vendor_id),

            # Vendor 3 - Book Haven Store
            ("Data Science and AI Handbook", "Books", Decimal("45.00"), 60, 15, vendors[2].vendor_id),
            ("Modern Web Architecture with FastAPI", "Books", Decimal("39.99"), 40, 10, vendors[2].vendor_id),
            ("The Art of Scalable Cloud Computing", "Books", Decimal("52.50"), 30, 8, vendors[2].vendor_id),

            # Vendor 4 - Urban Home Comforts
            ("Ergonomic Lumbar Support Office Chair", "Home & Kitchen", Decimal("185.00"), 18, 5, vendors[3].vendor_id),
            ("Cold Brew Espresso & Coffee Maker", "Home & Kitchen", Decimal("64.99"), 28, 8, vendors[3].vendor_id),
            ("Aroma Diffuser with LED Ambiance", "Home & Kitchen", Decimal("34.50"), 7, 10, vendors[3].vendor_id), # Low stock example

            # Vendor 5 - Glow Cosmetics & Spa
            ("Hydrating Vitamin C Facial Serum", "Beauty & Personal Care", Decimal("28.00"), 55, 15, vendors[4].vendor_id),
            ("Organic Herbal Moisturizing Cream", "Beauty & Personal Care", Decimal("24.50"), 10, 10, vendors[4].vendor_id), # Normal stock
            ("Exfoliating Mineral Body Scrub", "Beauty & Personal Care", Decimal("19.99"), 0, 10, vendors[4].vendor_id), # Out of stock example
        ]

        products = []
        for name, cat, price, stock, reorder, v_id in products_data:
            prod = Product(
                product_name=name,
                category=cat,
                price=price,
                stock=stock,
                vendor_id=v_id
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)

            inv = Inventory(
                product_id=prod.product_id,
                current_stock=stock,
                warehouse="Central Distribution Hub",
                reorder_level=reorder
            )
            db.add(inv)
            db.commit()
            products.append(prod)

        print(f"Created {len(products)} products and linked inventory records.")

        # 4. Seed 35+ Transactions with varying dates (last 21 days)
        print("Seeding 35+ realistic sales transactions...")
        now = datetime.now()
        # Seed sales transactions distributed across days
        transactions_to_add = [
            # Day -20
            (products[0], 2, now - timedelta(days=20, hours=4)),
            (products[3], 4, now - timedelta(days=20, hours=2)),
            # Day -18
            (products[6], 3, now - timedelta(days=18, hours=5)),
            (products[9], 1, now - timedelta(days=18, hours=1)),
            # Day -16
            (products[1], 2, now - timedelta(days=16, hours=6)),
            (products[12], 5, now - timedelta(days=16, hours=3)),
            # Day -14
            (products[4], 3, now - timedelta(days=14, hours=7)),
            (products[7], 2, now - timedelta(days=14, hours=2)),
            (products[2], 1, now - timedelta(days=14, hours=1)),
            # Day -12
            (products[10], 2, now - timedelta(days=12, hours=8)),
            (products[13], 4, now - timedelta(days=12, hours=3)),
            # Day -10
            (products[5], 2, now - timedelta(days=10, hours=5)),
            (products[0], 1, now - timedelta(days=10, hours=2)),
            (products[8], 2, now - timedelta(days=10, hours=1)),
            # Day -8
            (products[3], 6, now - timedelta(days=8, hours=6)),
            (products[1], 3, now - timedelta(days=8, hours=4)),
            (products[12], 3, now - timedelta(days=8, hours=2)),
            # Day -6
            (products[2], 2, now - timedelta(days=6, hours=7)),
            (products[9], 1, now - timedelta(days=6, hours=3)),
            (products[6], 4, now - timedelta(days=6, hours=1)),
            # Day -5
            (products[4], 5, now - timedelta(days=5, hours=8)),
            (products[10], 1, now - timedelta(days=5, hours=4)),
            (products[7], 3, now - timedelta(days=5, hours=2)),
            # Day -4
            (products[0], 3, now - timedelta(days=4, hours=6)),
            (products[13], 2, now - timedelta(days=4, hours=3)),
            # Day -3
            (products[1], 2, now - timedelta(days=3, hours=7)),
            (products[3], 5, now - timedelta(days=3, hours=5)),
            (products[12], 4, now - timedelta(days=3, hours=2)),
            # Day -2
            (products[5], 3, now - timedelta(days=2, hours=8)),
            (products[8], 2, now - timedelta(days=2, hours=4)),
            (products[2], 1, now - timedelta(days=2, hours=1)),
            # Day -1
            (products[4], 4, now - timedelta(days=1, hours=7)),
            (products[9], 2, now - timedelta(days=1, hours=5)),
            (products[0], 2, now - timedelta(days=1, hours=2)),
            # Today
            (products[6], 5, now - timedelta(hours=5)),
            (products[1], 3, now - timedelta(hours=3)),
            (products[3], 7, now - timedelta(hours=1)),
        ]

        total_tx_count = 0
        total_revenue = Decimal("0.00")
        for prod, qty, tx_date in transactions_to_add:
            amt = prod.price * qty
            tx = Transaction(
                product_id=prod.product_id,
                vendor_id=prod.vendor_id,
                quantity=qty,
                amount=amt,
                transaction_date=tx_date
            )
            db.add(tx)
            total_tx_count += 1
            total_revenue += amt

        db.commit()
        print(f"Successfully seeded {total_tx_count} transactions with total revenue ${total_revenue:,.2f}.")
        print("Seed data completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
