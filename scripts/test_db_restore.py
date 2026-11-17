import pymysql
import subprocess

def test_restore():
    conn = pymysql.connect(host='localhost', user='root', password='Oct2005bday@', port=3306)
    cursor = conn.cursor()
    cursor.execute('DROP DATABASE IF EXISTS shopsense_restore_test;')
    cursor.execute('CREATE DATABASE shopsense_restore_test CHARACTER SET utf8mb4;')
    conn.commit()

    with open(r'D:\ShopSense_Backup\shopsense_dump_20261115_201000.sql', 'r', encoding='utf-8') as f:
        res = subprocess.run(
            [r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe', '-u', 'root', '-pOct2005bday@', 'shopsense_restore_test'],
            stdin=f, capture_output=True, text=True
        )
    print('Restore return code:', res.returncode)
    if res.stderr:
        print('Restore stderr:', res.stderr[:300])

    cursor.execute('SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME', ('shopsense',))
    orig_tables = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME', ('shopsense_restore_test',))
    restored_tables = [row[0] for row in cursor.fetchall()]

    print(f'Original tables ({len(orig_tables)}):', orig_tables)
    print(f'Restored tables ({len(restored_tables)}):', restored_tables)
    assert orig_tables == restored_tables, 'Tables list mismatch!'

    all_matched = True
    for t in orig_tables:
        cursor.execute(f'SELECT COUNT(*) FROM shopsense.{t}')
        orig_cnt = cursor.fetchone()[0]
        cursor.execute(f'SELECT COUNT(*) FROM shopsense_restore_test.{t}')
        rest_cnt = cursor.fetchone()[0]
        status = 'MATCH' if orig_cnt == rest_cnt else 'MISMATCH'
        if orig_cnt != rest_cnt:
            all_matched = False
        print(f'  Table {t:28}: original={orig_cnt:5}, restored={rest_cnt:5} [{status}]')

    print('All tables and counts matched 100%:', all_matched)

    cursor.execute('DROP DATABASE shopsense_restore_test;')
    conn.commit()
    conn.close()
    print('Temporary database shopsense_restore_test dropped successfully.')

if __name__ == '__main__':
    test_restore()
