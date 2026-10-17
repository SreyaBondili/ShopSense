import pymysql

conn = pymysql.connect(
    host="localhost", port=3306,
    user="root", password="Oct2005bday@",
    database="shopsense"
)
cur = conn.cursor()

print("=" * 60)
print("           SHOPSENSE DATABASE - ALL DATA")
print("=" * 60)

# USERS
print("\n>>> USERS TABLE")
cur.execute("SELECT user_id, full_name, email, role, is_active FROM users")
rows = cur.fetchall()
print(f"{'ID':<5} {'Name':<25} {'Email':<30} {'Role':<8} Active")
print("-" * 75)
for r in rows:
    print(f"{r[0]:<5} {str(r[1]):<25} {str(r[2]):<30} {str(r[3]):<8} {r[4]}")

# VENDORS
print("\n>>> VENDORS TABLE")
cur.execute("SELECT vendor_id, business_name, owner_name, category, status FROM vendors")
rows = cur.fetchall()
print(f"{'ID':<5} {'Business Name':<25} {'Owner':<20} {'Category':<15} Status")
print("-" * 80)
for r in rows:
    print(f"{r[0]:<5} {str(r[1]):<25} {str(r[2]):<20} {str(r[3]):<15} {r[4]}")

# PRODUCTS
print("\n>>> PRODUCTS TABLE")
cur.execute("SELECT product_id, product_name, category, price, stock, vendor_id FROM products")
rows = cur.fetchall()
print(f"{'ID':<5} {'Product Name':<28} {'Category':<15} {'Price':<10} {'Stock':<8} VendorID")
print("-" * 80)
for r in rows:
    print(f"{r[0]:<5} {str(r[1]):<28} {str(r[2]):<15} {str(r[3]):<10} {r[4]:<8} {r[5]}")

# INVENTORY
print("\n>>> INVENTORY TABLE")
cur.execute("SELECT inventory_id, product_id, current_stock, warehouse, reorder_level FROM inventory")
rows = cur.fetchall()
print(f"{'ID':<5} {'ProductID':<10} {'Stock':<8} {'Warehouse':<20} ReorderLevel")
print("-" * 60)
for r in rows:
    print(f"{r[0]:<5} {r[1]:<10} {r[2]:<8} {str(r[3]):<20} {r[4]}")

# TRANSACTIONS
print("\n>>> TRANSACTIONS TABLE")
cur.execute("SELECT transaction_id, product_id, vendor_id, quantity, amount, transaction_date FROM transactions")
rows = cur.fetchall()
print(f"{'ID':<5} {'ProdID':<8} {'VendID':<8} {'Qty':<6} {'Amount':<12} Date")
print("-" * 60)
for r in rows:
    print(f"{r[0]:<5} {r[1]:<8} {r[2]:<8} {r[3]:<6} {str(r[4]):<12} {r[5]}")

print("\n" + "=" * 60)
print("SUMMARY:")
for table in ["users", "vendors", "products", "inventory", "transactions"]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    print(f"  {table:<15} : {count} records")
print("=" * 60)

conn.close()
