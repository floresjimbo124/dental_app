import sqlite3
import os

def migrate_database():
    """Migrate existing database to include new patient fields"""
    DB_FILE = "dental.db"
    
    if not os.path.exists(DB_FILE):
        print("Database file not found. Creating new database...")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # List of new columns to add
    new_columns = [
        ('Religion', 'TEXT'),
        ('HomeAddress', 'TEXT'),
        ('Occupation', 'TEXT'),
        ('DentalInsurance', 'TEXT'),
        ('EffectiveDate', 'TEXT'),
        ('ParentGuardianName', 'TEXT'),
        ('ParentGuardianOccupation', 'TEXT'),
        ('ReferralSource', 'TEXT'),
        ('ConsultationReason', 'TEXT'),
        ('DentalHistory', 'TEXT'),
        ('PreviousDentist', 'TEXT'),
        ('LastDentalVisit', 'TEXT'),
        ('Sex', 'TEXT'),
        ('Nickname', 'TEXT'),
        ('Age', 'TEXT'),
        ('Nationality', 'TEXT'),
        ('GoodHealth', 'TEXT'),
        ('MedicalTreatment', 'TEXT'),
        ('TreatmentCondition', 'TEXT'),
        ('SeriousIllness', 'TEXT'),
        ('SurgicalOperation', 'TEXT'),
        ('Hospitalized', 'TEXT'),
        ('HospitalizationDetails', 'TEXT'),
        ('PrescriptionMedication', 'TEXT'),
        ('NonPrescriptionMedication', 'TEXT'),
        ('TobaccoUse', 'TEXT'),
        ('AlcoholDrugUse', 'TEXT'),
        ('AllergicLocalAnesthetic', 'TEXT'),
        ('AllergicPenicillin', 'TEXT'),
        ('AllergicAntibiotics', 'TEXT'),
        ('AllergicSulfaDrugs', 'TEXT'),
        ('AllergicAspirin', 'TEXT'),
        ('AllergicLatex', 'TEXT'),
        ('AllergicOthers', 'TEXT'),
        ('BleedingTime', 'TEXT'),
        ('Pregnant', 'TEXT'),
        ('Nursing', 'TEXT'),
        ('BirthPills', 'TEXT'),
        ('BloodType', 'TEXT'),
        ('BloodPressure', 'TEXT')
    ]
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(Patients)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    
    # Add new columns if they don't exist
    for column_name, column_type in new_columns:
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE Patients ADD COLUMN {column_name} {column_type}")
                print(f"Added column: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"Error adding column {column_name}: {e}")
    
    try:
        cursor.execute("ALTER TABLE DentalCharts ADD COLUMN SliceColors TEXT")
        print("SliceColors column added.")
    except Exception as e:
        print("Column may already exist or error occurred:", e)
    
    conn.commit()
    conn.close()
    print("Database migration completed!")

if __name__ == "__main__":
    migrate_database() 