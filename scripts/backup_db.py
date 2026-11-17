import pymysql
import json
import datetime
from decimal import Decimal

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Oct2005bday@',
    database='shopsense',
    port=3306
)
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute('SHOW TABLES')
tables = [list(r.values())[0] for r in cur.fetchall()]
dump = {}

for t in tables:
    cur.execute(f"SELECT * FROM `{t}`")
    rows = cur.fetchall()
    dump[t] = rows

def serializer(o):
    if isinstance(o, (datetime.datetime, datetime.date)):
        return o.isoformat()
    if isinstance(o, Decimal):
        return float(o)
    return str(o)

backup_path = "C:/Users/Dell/.gemini/antigravity/scratch/ShopSense/data/backups/shopsense_mysql_backup_20261116_114500.json"
with open(backup_path, "w", encoding="utf-8") as f:
    json.dump(dump, f, default=serializer, indent=2)

print("DATABASE BACKUP SUCCESSFUL!")
print(f"File: {backup_path}")
print("Table Row Counts:")
for t in tables:
    print(f"  {t}: {len(dump[t])}")

conn.close()
