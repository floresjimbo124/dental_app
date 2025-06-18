import sqlite3
import os

def migrate_database():
    """Migrate the database to include the new Patients table and migrate existing data"""
    
    # Check if dental.db exists
    if not os.path.exists('dental.db'):
        print("Database file not found. Creating new database...")
        return
    
    conn = sqlite3.connect('dental.db')
    cursor = conn.cursor()
    
    try:
        # Create Patients table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Patients (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL UNIQUE,
                Contact TEXT NOT NULL,
                Email TEXT,
                DateOfBirth TEXT,
                Address TEXT,
                EmergencyContact TEXT,
                MedicalHistory TEXT,
                CreatedDate TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Get all unique patients from appointments
        cursor.execute("""
            SELECT DISTINCT PatientName, Contact 
            FROM Appointments 
            ORDER BY PatientName
        """)
        
        unique_patients = cursor.fetchall()
        print(f"Found {len(unique_patients)} unique patients in appointments")
        
        # Insert each unique patient into the Patients table
        migrated_count = 0
        for patient_name, contact in unique_patients:
            try:
                cursor.execute("""
                    INSERT INTO Patients (Name, Contact)
                    VALUES (?, ?)
                """, (patient_name, contact))
                print(f"Created patient record for: {patient_name}")
                migrated_count += 1
            except sqlite3.IntegrityError:
                print(f"Patient {patient_name} already exists, skipping...")
        
        conn.commit()
        print(f"Successfully migrated {migrated_count} patients to the Patients table.")
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM Patients")
        final_patient_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Appointments")
        appointment_count = cursor.fetchone()[0]
        
        print(f"\nDatabase migration completed successfully!")
        print(f"Total patients: {final_patient_count}")
        print(f"Total appointments: {appointment_count}")
        
        # Show all patients
        print("\nAll patients in database:")
        cursor.execute("SELECT Name, Contact FROM Patients ORDER BY Name")
        patients = cursor.fetchall()
        for patient in patients:
            print(f"  - {patient[0]} ({patient[1]})")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 