import sqlite3

conn = sqlite3.connect('dental.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM DentalCharts')
rows = cursor.fetchall()

print('DentalCharts table:')
for row in rows:
    print(row)

conn.close() 