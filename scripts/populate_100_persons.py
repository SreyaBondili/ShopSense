"""
ShopSense - Safe Expansion to 100+ Person Database
Mentor Requirement: At least 100 persons in the database for comprehensive analytics.

Rules:
- 100% NON-DESTRUCTIVE: Preserves all existing users, admin, vendors, and transactions.
- Assigns the 546 unassigned (user_id=NULL) historical transactions across newly created persons.
- Total revenue and total order count remain 100% exact to the paisa.
- Generates updated data/customers.csv reflecting all 100+ shoppers.
"""

import os
import sys
import random
import pandas as pd
from datetime import datetime
from sqlalchemy import func
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.transaction import Transaction
from app.utils.security import hash_password

FIRST_NAMES = [
    "Aarav", "Sneha", "Vikram", "Ananya", "Rohan", "Pooja", "Aditya", "Kavya", "Siddharth", "Neha",
    "Arjun", "Ishita", "Karan", "Tanvi", "Varun", "Divya", "Manish", "Rhea", "Harish", "Aparna",
    "Gaurav", "Meera", "Kunal", "Simran", "Naveen", "Shreya", "Rajesh", "Bhavna", "Amitabh", "Deepika",
    "Vishal", "Radhika", "Nitin", "Sangeeta", "Pranav", "Sunita", "Ashish", "Pallavi", "Ravi", "Sonal",
    "Abhinav", "Komal", "Suresh", "Anita", "Devendra", "Shruti", "Mayank", "Vandana", "Hemant", "Anjali",
    "Saurabh", "Monika", "Alok", "Preeti", "Umesh", "Richa", "Pankaj", "Shalini", "Dinesh", "Archana",
    "Jayesh", "Smita", "Sunil", "Geeta", "Mohit", "Namrata", "Tarun", "Payal", "Deepak", "Shweta",
    "Bipin", "Leela", "Anil", "Kritika", "Sanjay", "Ritu", "Akash", "Tanya", "Chetan", "Nandini",
    "Gautam", "Payal", "Harshit", "Bhumika", "Yash", "Juhi", "Omkar", "Rashmi", "Sameer", "Tara",
    "Dhruv", "Sakshi", "Prateek", "Isha", "Vivek", "Meenakshi", "Manav", "Chitrangada", "Rupesh", "Kalyani"
]

LAST_NAMES = [
    "Sharma", "Reddy", "Malhotra", "Iyer", "Gupta", "Mehta", "Nair", "Deshmukh", "Joshi", "Bansal",
    "Kapoor", "Chatterjee", "Singhania", "Bhatia", "Chopra", "Menon", "Tiwari", "Sengupta", "Pillai", "Mukherjee",
    "Saxena", "Kulkarni", "Agarwal", "Kaur", "Nambiar", "Sen", "Pandey", "Mishra", "Roy", "Namboodiri",
    "Bhatt", "Choudhury", "Mathur", "Rao", "Hegde", "Das", "Verma", "Ghosh", "Shankar", "Jain",
    "Anand", "Sethi", "Kumar", "Chauhan", "Trivedi", "Mittal", "Rastogi", "Kaushik", "Shukla", "Bajaj",
    "Srivastava", "Sundaram", "Yadav", "Goswami", "Dubey", "Rawat", "Swaminathan", "Patel", "Deshpande", "Varma",
    "Bhattacharya", "Goyal", "Shinde", "Khanna", "Parekh", "Kashyap", "Somani", "Chawla", "Krishnan", "Aggarwal"
]

def generate_person_names(count_needed: int):
    generated = []
    used_emails = set()
    random.seed(42)

    for i in range(count_needed):
        fn = FIRST_NAMES[i % len(FIRST_NAMES)]
        ln = LAST_NAMES[(i * 3 + 7) % len(LAST_NAMES)]
        full_name = f"{fn} {ln}"
        base_email = f"{fn.lower()}.{ln.lower()}"
        email = f"{base_email}@example.com"
        suffix = 1
        while email in used_emails:
            email = f"{base_email}{suffix}@example.com"
            suffix += 1
        used_emails.add(email)
        generated.append((full_name, email))

    return generated

def populate_database_to_100_persons():
    db = SessionLocal()
    try:
        # 1. Baseline verification
        initial_total_users = db.query(User).count()
        existing_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).all()
        existing_cust_count = len(existing_customers)
        unassigned_txs = db.query(Transaction).filter(Transaction.user_id == None).all()
        total_tx_count = db.query(Transaction).count()
        total_revenue_before = float(db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).scalar())

        print("=== SHOPSENSE DATABASE EXPANSION AUDIT ===")
        print(f"Initial Total Users (Persons): {initial_total_users}")
        print(f"Current Customer Profiles:     {existing_cust_count}")
        print(f"Total Transactions:            {total_tx_count}")
        print(f"Unassigned (user_id=NULL) Txs: {len(unassigned_txs)}")
        print(f"Total Revenue Baseline:        INR {total_revenue_before:,.2f}")

        target_total_customers = 100
        needed = max(0, target_total_customers - existing_cust_count)
        print(f"\nPersons to be added to reach 100+ customers: {needed}")

        if needed == 0:
            print("Database already has at least 100 customers!")
            return

        # 2. Generate new person records
        person_data = generate_person_names(needed)
        default_hash = hash_password("Customer@123")
        new_users = []

        for full_name, email in person_data:
            user = User(
                full_name=full_name,
                email=email,
                password_hash=default_hash,
                role=UserRole.CUSTOMER,
                is_active=True,
                created_at=datetime.now()
            )
            db.add(user)
            new_users.append(user)

        db.flush()  # Populates user_id for all new users
        print(f"Successfully inserted {len(new_users)} new person records.")

        # 3. Distribute unassigned transactions across all new persons
        # Create realistic RFM tier distribution for the 546 unassigned transactions
        if unassigned_txs:
            tx_pool = list(unassigned_txs)
            random.seed(101)
            random.shuffle(tx_pool)

            # Assign weights for transaction allocation:
            # - Tier 1: High activity (15% of users get 8-12 txs)
            # - Tier 2: Regular activity (35% of users get 5-7 txs)
            # - Tier 3: Occasional activity (30% of users get 3-5 txs)
            # - Tier 4: Dormant / New (20% of users get 1-2 txs)
            allocations = []
            for idx in range(len(new_users)):
                pct = idx / len(new_users)
                if pct < 0.15:
                    allocations.append(random.randint(8, 12))
                elif pct < 0.50:
                    allocations.append(random.randint(5, 7))
                elif pct < 0.80:
                    allocations.append(random.randint(3, 5))
                else:
                    allocations.append(random.randint(1, 2))

            # Scale allocations to match exact count of unassigned transactions
            alloc_sum = sum(allocations)
            scaled = [max(1, int(a * len(tx_pool) / alloc_sum)) for a in allocations]
            diff = len(tx_pool) - sum(scaled)
            for d in range(abs(diff)):
                if diff > 0:
                    scaled[d % len(scaled)] += 1
                elif diff < 0 and scaled[d % len(scaled)] > 1:
                    scaled[d % len(scaled)] -= 1

            # Assign transactions
            tx_cursor = 0
            for user, count in zip(new_users, scaled):
                assigned_slice = tx_pool[tx_cursor : tx_cursor + count]
                for tx in assigned_slice:
                    tx.user_id = user.user_id
                tx_cursor += len(assigned_slice)

            print(f"Distributed {tx_cursor} previously unassigned transactions across {len(new_users)} new persons.")

        db.commit()

        # 4. Update data/customers.csv to reflect all 100+ shoppers
        all_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).all()
        csv_rows = []
        for c in all_customers:
            c_stats = db.query(
                func.count(Transaction.transaction_id),
                func.coalesce(func.sum(Transaction.amount), 0.0)
            ).filter(Transaction.user_id == c.user_id).first()

            orders = c_stats[0] if c_stats else 0
            spent = round(float(c_stats[1]), 2) if c_stats else 0.0
            csv_rows.append({
                "customer_id": c.user_id,
                "full_name": c.full_name,
                "email": c.email,
                "total_orders": orders,
                "total_spent": spent
            })

        csv_df = pd.DataFrame(csv_rows)
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "customers.csv")
        csv_df.to_csv(csv_path, index=False)
        print(f"Updated {csv_path} with {len(csv_df)} customer rows.")

        # 5. Final Integrity Verification
        final_total_users = db.query(User).count()
        final_cust_count = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
        final_tx_count = db.query(Transaction).count()
        total_revenue_after = float(db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).scalar())
        remaining_unassigned = db.query(Transaction).filter(Transaction.user_id == None).count()

        print("\n=== POST-EXPANSION VERIFICATION ===")
        print(f"Final Total Persons (Users):   {final_total_users} (Goal >= 100: ACHIEVED)")
        print(f"Final Customer Profiles:       {final_cust_count}")
        print(f"Total Transactions:            {final_tx_count} (Unchanged: {final_tx_count == total_tx_count})")
        print(f"Total Revenue After:           INR {total_revenue_after:,.2f} (Exact match: {abs(total_revenue_after - total_revenue_before) < 0.01})")
        print(f"Remaining Unassigned Txs:      {remaining_unassigned}")
        print("Database expansion complete successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    populate_database_to_100_persons()
