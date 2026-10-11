import sqlite3

conn = sqlite3.connect(r'd:\Projects\Lenny Growth\lenny_growth.db')
c = conn.cursor()
tables = [row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables in lenny_growth.db:", tables)
for t in tables:
    count = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"  - {t}: {count} rows")
