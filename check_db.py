import sqlite3

def check_database():
    """Check the database structure and data"""
    
    conn = sqlite3.connect('dental.db')
    cursor = conn.cursor()
    
    try:
        # Check table structure
        print("=== Database Tables ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"Table: {table[0]}")
            
            # Show table schema
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            print()
        
        # Check data counts
        print("=== Data Counts ===")
        cursor.execute("SELECT COUNT(*) FROM Patients")
        patient_count = cursor.fetchone()[0]
        print(f"Patients: {patient_count}")
        
        cursor.execute("SELECT COUNT(*) FROM Appointments")
        appointment_count = cursor.fetchone()[0]
        print(f"Appointments: {appointment_count}")
        
        # Show sample data
        print("\n=== Sample Patients ===")
        cursor.execute("SELECT * FROM Patients LIMIT 3")
        patients = cursor.fetchall()
        for patient in patients:
            print(f"ID: {patient[0]}, Name: {patient[1]}, Contact: {patient[2]}")
        
        print("\n=== Sample Appointments ===")
        cursor.execute("SELECT * FROM Appointments LIMIT 3")
        appointments = cursor.fetchall()
        for appointment in appointments:
            print(f"ID: {appointment[0]}, Patient: {appointment[1]}, Date: {appointment[3]}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database() 