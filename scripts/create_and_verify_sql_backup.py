import os
import sys
import pymysql
import datetime
from decimal import Decimal

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "Oct2005bday@"
DB_NAME = "shopsense"
TEMP_DB = "shopsense_verify_temp"
BACKUP_SQL_PATH = os.path.abspath("data/backups/shopsense_full_backup_20261116_132500.sql")

def format_sql_value(val):
    if val is None:
        return "NULL"
    elif isinstance(val, (int, float, Decimal)):
        return str(val)
    elif isinstance(val, (datetime.datetime, datetime.date)):
        return f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'"
    elif isinstance(val, bytes):
        return f"X'{val.hex()}'"
    else:
        escaped = str(val).replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"

def generate_full_sql_dump(conn, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    cur = conn.cursor()
    cur.execute("SHOW TABLES;")
    tables = [r[0] for r in cur.fetchall()]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("-- ShopSense Complete MySQL Schema and Data Backup\n")
        f.write(f"-- Generated: {datetime.datetime.now().isoformat()}\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
        f.write("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';\n")
        f.write("SET NAMES utf8mb4;\n\n")

        for table in tables:
            # 1. Schema
            cur.execute(f"SHOW CREATE TABLE `{table}`;")
            create_stmt = cur.fetchone()[1]
            f.write(f"--\n-- Structure for table `{table}`\n--\n")
            f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
            f.write(f"{create_stmt};\n\n")

            # 2. Data
            cur.execute(f"SELECT * FROM `{table}`;")
            rows = cur.fetchall()
            if rows:
                col_names = [desc[0] for desc in cur.description]
                cols_str = ", ".join([f"`{c}`" for c in col_names])
                f.write(f"--\n-- Dumping data for table `{table}` ({len(rows)} records)\n--\n")
                f.write(f"LOCK TABLES `{table}` WRITE;\n")
                
                # Batch inserts
                batch_size = 100
                for i in range(0, len(rows), batch_size):
                    batch = rows[i:i+batch_size]
                    vals_list = []
                    for row in batch:
                        vals_str = ", ".join([format_sql_value(v) for v in row])
                        vals_list.append(f"({vals_str})")
                    f.write(f"INSERT INTO `{table}` ({cols_str}) VALUES\n" + ",\n".join(vals_list) + ";\n")
                
                f.write("UNLOCK TABLES;\n\n")

        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")
    print(f"[OK] Full SQL backup generated successfully: {filepath}")
    print(f"     File size: {os.path.getsize(filepath):,} bytes")
    return tables

def restore_and_verify(filepath, original_tables):
    print("\n--- BEGINNING RESTORE VERIFICATION INTO TEMPORARY DATABASE ---")
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, port=3306)
    cur = conn.cursor()

    # 1. Create separate temporary database
    print(f"[1/4] Creating temporary verification database `{TEMP_DB}`...")
    cur.execute(f"DROP DATABASE IF EXISTS `{TEMP_DB}`;")
    cur.execute(f"CREATE DATABASE `{TEMP_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cur.execute(f"USE `{TEMP_DB}`;")
    conn.commit()

    # 2. Execute SQL dump into temporary database
    print(f"[2/4] Executing SQL dump into `{TEMP_DB}`...")
    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Parse and execute multi-statements
    statements = []
    current = []
    in_lock = False
    for line in sql_content.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("--"):
            continue
        current.append(line)
        if trimmed.endswith(";"):
            statements.append("\n".join(current))
            current = []

    print(f"     Executing {len(statements)} SQL statements...")
    for stmt in statements:
        if stmt.strip():
            cur.execute(stmt)
    conn.commit()
    print("[OK] All SQL statements executed successfully into temporary database.")

    # 3. Compare tables and row counts
    print(f"[3/4] Comparing schema and row counts between `{DB_NAME}` and `{TEMP_DB}`...")
    cur.execute(f"SHOW TABLES IN `{TEMP_DB}`;")
    temp_tables = [r[0] for r in cur.fetchall()]

    assert set(temp_tables) == set(original_tables), f"Table set mismatch: {set(original_tables) - set(temp_tables)}"
    print(f"[PASS] Table count matches exactly ({len(temp_tables)} tables).")

    all_matched = True
    print(f"\n{'Table Name':<30} | {'Source Rows':<12} | {'Restored Rows':<14} | {'Verification'}")
    print("-" * 72)
    for t in original_tables:
        cur.execute(f"SELECT COUNT(*) FROM `{DB_NAME}`.`{t}`;")
        src_cnt = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(*) FROM `{TEMP_DB}`.`{t}`;")
        rst_cnt = cur.fetchone()[0]
        match = (src_cnt == rst_cnt)
        if not match:
            all_matched = False
        print(f"{t:<30} | {src_cnt:<12} | {rst_cnt:<14} | {'PASS (EXACT)' if match else 'FAIL'}")
    print("-" * 72)

    assert all_matched, "Row count mismatch between source and restored database!"
    print("[PASS] All table row counts match 100% identically!")

    # 4. Cleanup temporary database
    print(f"\n[4/4] Cleaning up temporary database `{TEMP_DB}`...")
    cur.execute(f"DROP DATABASE `{TEMP_DB}`;")
    conn.commit()
    conn.close()
    print(f"[OK] Temporary database `{TEMP_DB}` dropped cleanly.")
    print("[CONFIRMED] Source database `shopsense` remains completely intact and verified.\n")

if __name__ == "__main__":
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=3306)
    tables = generate_full_sql_dump(conn, BACKUP_SQL_PATH)
    conn.close()

    restore_and_verify(BACKUP_SQL_PATH, tables)
