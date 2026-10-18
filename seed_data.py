import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorStatus
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.transaction import Transaction
from app.utils.security import hash_password

def seed():
    db: Session = SessionLocal()
    rng = random.Random(42)  # Deterministic seed for repeatable, consistent analytics
    try:
        print("Starting ShopSense comprehensive database seeding...")

        # 1. Clear existing records to ensure fresh demo state
        print("Clearing old records...")
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.query(Transaction).delete()
        db.query(Inventory).delete()
        db.query(Product).delete()
        db.query(Vendor).delete()
        db.query(User).delete()
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        db.commit()

        # 2. Seed Users & Accounts
        print("Seeding Users (Admin, Customers, Vendors)...")
        # 2a. Platform Admin - Sreya Bondili
        admin_user = User(
            full_name="Sreya Bondili (Admin)",
            email="bsreya1610@gmail.com",
            password_hash=hash_password("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)

        # 2b. Customer Users
        customers_data = [
            ("Alice Johnson (Customer)", "customer@shopsense.com"),
            ("Rahul Verma", "rahul.verma@example.com"),
            ("Priya Patel", "priya.patel@example.com"),
            ("Carlos Mendez", "carlos.m@example.com"),
            ("Ananya Rao", "ananya.rao@example.com"),
        ]
        customer_users = []
        for name, email in customers_data:
            cust = User(
                full_name=name,
                email=email,
                password_hash=hash_password("Customer@123"),
                role=UserRole.CUSTOMER,
                is_active=True
            )
            db.add(cust)
            db.commit()
            db.refresh(cust)
            customer_users.append(cust)

        # 2c. Vendor Accounts (10 diverse vendors)
        vendor_profiles_data = [
            # (business_name, email, owner_name, category, phone, commission_rate, status)
            ("Apex Electronics", "techworld@example.com", "John Doe", "Electronics", "9876543210", Decimal("12.50"), VendorStatus.ACTIVE),
            ("Aura Fashion Hub", "trendsfashion@example.com", "Sarah Miller", "Fashion", "9876543211", Decimal("10.00"), VendorStatus.ACTIVE),
            ("Book Haven Store", "bookoasis@example.com", "Robert Clark", "Books", "9876543212", Decimal("8.50"), VendorStatus.ACTIVE),
            ("Urban Home Comforts", "homecomforts@example.com", "Emma Watson", "Home & Kitchen", "9876543213", Decimal("11.00"), VendorStatus.ACTIVE),
            ("Glow Cosmetics & Spa", "glowbeauty@example.com", "Priya Sharma", "Beauty & Personal Care", "9876543214", Decimal("14.00"), VendorStatus.ACTIVE),
            ("Nexus Smart Tech", "nexustech@example.com", "David Chen", "Electronics", "9876543215", Decimal("12.00"), VendorStatus.ACTIVE),
            ("Urban Stitch Apparel", "urbanstitch@example.com", "Liam Brown", "Fashion", "9876543216", Decimal("9.50"), VendorStatus.ACTIVE),
            ("Nordic Living Essentials", "nordicliving@example.com", "Olivia Davis", "Home & Kitchen", "9876543217", Decimal("10.50"), VendorStatus.ACTIVE),
            ("PureBotanica Organics", "purebotanica@example.com", "Sophia Taylor", "Beauty & Personal Care", "9876543218", Decimal("13.00"), VendorStatus.PENDING),  # Onboarding demo
            ("Horizon Academic Press", "horizonpress@example.com", "James Wilson", "Books", "9876543219", Decimal("8.00"), VendorStatus.SUSPENDED),  # Suspension guard demo
        ]

        vendors = []
        for b_name, email, owner, cat, phone, comm, v_status in vendor_profiles_data:
            v_user = User(
                full_name=owner,
                email=email,
                password_hash=hash_password("Vendor@123"),
                role=UserRole.VENDOR,
                is_active=(v_status != VendorStatus.SUSPENDED)
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
                commission_rate=comm,
                status=v_status,
                user_id=v_user.user_id
            )
            db.add(vendor)
            db.commit()
            db.refresh(vendor)
            vendors.append(vendor)

        print(f"Created {len(vendors)} vendors with associated user accounts.")

        # 3. Seed Products (40 diverse catalog products across 5 categories)
        print("Seeding 40 Products and Inventory records across warehouses...")
        # (product_name, category, price, stock, reorder_level, vendor_index, warehouse)
        products_catalog = [
            # Vendor 0: Apex Electronics
            ("Noise-Cancelling Wireless Headphones Pro", "Electronics", Decimal("149.99"), 45, 12, 0, "Central Distribution Hub"),
            ("Ultra-Slim RGB Mechanical Keyboard", "Electronics", Decimal("89.50"), 35, 10, 0, "Central Distribution Hub"),
            ("Smartwatch Series 7 Titanium", "Electronics", Decimal("249.00"), 28, 8, 0, "West Coast Logistics"),
            ("Thunderbolt 4 High-Speed USB Dock", "Electronics", Decimal("119.00"), 18, 5, 0, "Central Distribution Hub"),

            # Vendor 1: Aura Fashion Hub
            ("Organic Cotton Classic Graphic Tee", "Fashion", Decimal("29.99"), 85, 20, 1, "East Coast Fulfillment"),
            ("Classic Slim-Fit Stretch Denim Jeans", "Fashion", Decimal("59.95"), 55, 15, 1, "East Coast Fulfillment"),
            ("Lightweight Waterproof All-Weather Windbreaker", "Fashion", Decimal("89.00"), 38, 10, 1, "Central Distribution Hub"),
            ("Merino Wool Thermal Crewneck Sweater", "Fashion", Decimal("69.50"), 25, 8, 1, "East Coast Fulfillment"),

            # Vendor 2: Book Haven Store
            ("Data Science & AI Engineering Handbook", "Books", Decimal("49.99"), 65, 15, 2, "Central Distribution Hub"),
            ("Modern Web Architecture with FastAPI & React", "Books", Decimal("39.99"), 45, 10, 2, "Central Distribution Hub"),
            ("The Art of Scalable Cloud Computing", "Books", Decimal("54.50"), 32, 8, 2, "Southern Logistics Center"),
            ("Deep Learning Illustrated (Hardcover Edition)", "Books", Decimal("59.00"), 22, 6, 2, "Central Distribution Hub"),

            # Vendor 3: Urban Home Comforts
            ("Ergonomic Lumbar Support Mesh Office Chair", "Home & Kitchen", Decimal("199.99"), 22, 5, 3, "West Coast Logistics"),
            ("Cold Brew Precision Espresso Coffee Maker", "Home & Kitchen", Decimal("74.99"), 30, 8, 3, "Central Distribution Hub"),
            ("Ultrasonic Aroma Diffuser with Ambient LED", "Home & Kitchen", Decimal("34.50"), 6, 10, 3, "Central Distribution Hub"),  # Low stock
            ("Non-Stick Ceramic Cookware 10-Piece Set", "Home & Kitchen", Decimal("129.00"), 15, 5, 3, "Southern Logistics Center"),

            # Vendor 4: Glow Cosmetics & Spa
            ("Hydrating Vitamin C + Hyaluronic Facial Serum", "Beauty & Personal Care", Decimal("32.00"), 60, 15, 4, "East Coast Fulfillment"),
            ("Organic Herbal Daily Moisturizing Cream", "Beauty & Personal Care", Decimal("26.50"), 42, 10, 4, "East Coast Fulfillment"),
            ("Exfoliating Mineral Himalayan Body Scrub", "Beauty & Personal Care", Decimal("21.99"), 0, 10, 4, "Central Distribution Hub"),  # Out of stock
            ("Nourishing Botanical Night Repair Elixir", "Beauty & Personal Care", Decimal("38.00"), 25, 8, 4, "East Coast Fulfillment"),

            # Vendor 5: Nexus Smart Tech
            ("4K Ultra HD Dual-Monitor Webcam 60FPS", "Electronics", Decimal("89.99"), 40, 10, 5, "West Coast Logistics"),
            ("Wireless Ergonomic Vertical Mouse", "Electronics", Decimal("45.00"), 50, 12, 5, "West Coast Logistics"),
            ("Active Noise-Cancelling Bluetooth Earbuds", "Electronics", Decimal("79.99"), 30, 8, 5, "Central Distribution Hub"),
            ("Fast Magnetic Wireless Charging Pad 15W", "Electronics", Decimal("29.99"), 75, 15, 5, "West Coast Logistics"),

            # Vendor 6: Urban Stitch Apparel
            ("Tailored Casual Linen Blend Button-Down", "Fashion", Decimal("49.99"), 45, 12, 6, "East Coast Fulfillment"),
            ("Athletic Breathable Performance Joggers", "Fashion", Decimal("39.95"), 60, 15, 6, "Central Distribution Hub"),
            ("Unisex Heavyweight Fleece Pullover Hoodie", "Fashion", Decimal("54.00"), 35, 10, 6, "East Coast Fulfillment"),
            ("Seamless Comfort Yoga Leggings", "Fashion", Decimal("34.99"), 50, 12, 6, "East Coast Fulfillment"),

            # Vendor 7: Nordic Living Essentials
            ("Minimalist Solid Oak Bedside Lamp with Touch Dimmer", "Home & Kitchen", Decimal("49.50"), 25, 8, 7, "Central Distribution Hub"),
            ("Stainless Steel Double-Wall Thermal French Press", "Home & Kitchen", Decimal("42.00"), 35, 10, 7, "West Coast Logistics"),
            ("Natural Bamboo Cutlery & Cutting Board Trio", "Home & Kitchen", Decimal("28.00"), 40, 10, 7, "Southern Logistics Center"),
            ("Cast Iron Enamelled Dutch Oven 5.5 Qt", "Home & Kitchen", Decimal("89.99"), 12, 5, 7, "Central Distribution Hub"),

            # Vendor 8: PureBotanica Organics (Pending vendor demo)
            ("Organic Rosewater Balancing Facial Mist", "Beauty & Personal Care", Decimal("18.50"), 50, 10, 8, "East Coast Fulfillment"),
            ("Vegan Cold-Pressed Argan Hair Oil 100ml", "Beauty & Personal Care", Decimal("24.00"), 40, 8, 8, "East Coast Fulfillment"),
            ("Charcoal Clarifying Detox Detox Clay Mask", "Beauty & Personal Care", Decimal("22.50"), 30, 8, 8, "East Coast Fulfillment"),
            ("Pure Lavender Aromatherapy Essential Oil", "Beauty & Personal Care", Decimal("15.00"), 60, 12, 8, "East Coast Fulfillment"),

            # Vendor 9: Horizon Academic Press (Suspended vendor demo)
            ("Algorithms & Data Structures: A Practical Guide", "Books", Decimal("55.00"), 25, 6, 9, "Central Distribution Hub"),
            ("Microservices Architecture with Docker & K8s", "Books", Decimal("48.00"), 30, 8, 9, "Central Distribution Hub"),
            ("Database Internals & Storage Engines", "Books", Decimal("62.50"), 20, 5, 9, "Southern Logistics Center"),
            ("Designing Distributed Cloud Systems", "Books", Decimal("58.00"), 18, 5, 9, "Central Distribution Hub"),
        ]

        products = []
        for name, cat, price, stock, reorder, v_idx, wh in products_catalog:
            prod = Product(
                product_name=name,
                category=cat,
                price=price,
                stock=stock,
                vendor_id=vendors[v_idx].vendor_id
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)

            inv = Inventory(
                product_id=prod.product_id,
                current_stock=stock,
                warehouse=wh,
                reorder_level=reorder
            )
            db.add(inv)
            db.commit()
            products.append(prod)

        print(f"Created {len(products)} products and linked inventory records.")

        # 4. Seed 220+ Realistic Transactions spanning the last 60 days
        print("Seeding 220+ realistic sales transactions spanning the last 60 days...")
        now = datetime.now()
        active_products = [p for p in products if p.vendor_id in [v.vendor_id for v in vendors[:8]]]  # Transactions for active vendors

        total_tx_count = 0
        total_revenue = Decimal("0.00")

        # Generate realistic distribution: 3 to 6 transactions per day for 60 days
        for day_offset in range(59, -1, -1):
            day_date = now - timedelta(days=day_offset)
            # Weekend surge: Saturdays and Sundays get 5-8 transactions, weekdays get 3-5
            is_weekend = (day_date.weekday() >= 5)
            tx_count_today = rng.randint(5, 8) if is_weekend else rng.randint(3, 5)

            for _ in range(tx_count_today):
                # Pick a product with slight bias towards popular electronics/fashion
                prod = rng.choice(active_products)
                qty = rng.choices([1, 2, 3, 4, 5], weights=[50, 30, 12, 5, 3])[0]
                tx_time = day_date.replace(
                    hour=rng.randint(8, 22),
                    minute=rng.randint(0, 59),
                    second=rng.randint(0, 59)
                )
                amt = prod.price * qty
                chosen_cust = rng.choice(customer_users)

                tx = Transaction(
                    product_id=prod.product_id,
                    vendor_id=prod.vendor_id,
                    user_id=chosen_cust.user_id,
                    quantity=qty,
                    amount=amt,
                    transaction_date=tx_time
                )
                db.add(tx)
                total_tx_count += 1
                total_revenue += amt

        db.commit()
        print(f"Successfully seeded {total_tx_count} transactions with total revenue ${total_revenue:,.2f}.")
        print("ShopSense database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
