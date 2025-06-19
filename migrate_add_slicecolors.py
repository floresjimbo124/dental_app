import sqlite3

conn = sqlite3.connect('dental.db')
cursor = conn.cursor()

try:
        cursor.execute("ALTER TABLE DentalCharts ADD COLUMN SliceColors TEXT")
        print("SliceColors column added.")
except Exception as e:
        print("Column may already exist or error occurred:", e)

conn.commit()
conn.close()