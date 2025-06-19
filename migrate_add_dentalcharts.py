import sqlite3

conn = sqlite3.connect('dental.db')
cursor = conn.cursor()

# Create DentalCharts table with SliceColors column if it does not exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS DentalCharts (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        PatientID INTEGER NOT NULL,
        ToothNumber TEXT NOT NULL,
        Condition TEXT,
        Treatment TEXT,
        Notes TEXT,
        ExamDate TEXT DEFAULT CURRENT_TIMESTAMP,
        SliceColors TEXT,
        FOREIGN KEY (PatientID) REFERENCES Patients (ID),
        UNIQUE(PatientID, ToothNumber)
    )
''')

conn.commit()
conn.close()
print('DentalCharts table ensured in dental.db') 