import sqlite3

conn = sqlite3.connect('dental.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS TreatmentRecords (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        PatientID INTEGER NOT NULL,
        DateOfTreatment TEXT NOT NULL,
        ToothNumber TEXT,
        Procedure TEXT,
        DentistName TEXT,
        AmountCharged REAL,
        AmountPaid REAL,
        Balance REAL,
        NextAppointment TEXT,
        FOREIGN KEY (PatientID) REFERENCES Patients (ID)
    )
''')

conn.commit()
conn.close()
print('TreatmentRecords table ensured in dental.db') 