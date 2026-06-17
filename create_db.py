import sqlite3

conn = sqlite3.connect("pucc.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE certificates(
    certificate_no TEXT PRIMARY KEY,
    vehicle_no TEXT,
    fuel TEXT,
    fee REAL,
    date TEXT,
    time TEXT,
    saved_at TEXT,
    validity_upto TEXT,
    actual_charge REAL
)
""")

conn.commit()
conn.close()

print("Database created successfully!")