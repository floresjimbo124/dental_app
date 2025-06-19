import sqlite3
import os

def check_database():
    """Check the database structure and verify all patient fields are present"""
    DB_FILE = "dental.db"
    
    if not os.path.exists(DB_FILE):
        print("Database file not found.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check Patients table structure
    cursor.execute("PRAGMA table_info(Patients)")
    columns = cursor.fetchall()
    
    print("Patients table columns:")
    print("-" * 50)
    for column in columns:
        print(f"{column[1]} ({column[2]})")
    
    # Check if all required columns exist
    required_columns = [
        'ID', 'Name', 'Contact', 'Email', 'DateOfBirth', 'Address', 
        'EmergencyContact', 'MedicalHistory', 'Religion', 'HomeAddress', 
        'Occupation', 'DentalInsurance', 'EffectiveDate', 'ParentGuardianName', 
        'ParentGuardianOccupation', 'ReferralSource', 'ConsultationReason', 
        'DentalHistory', 'PreviousDentist', 'LastDentalVisit', 'Sex', 'Nickname', 
        'Age', 'Nationality', 'GoodHealth', 'MedicalTreatment', 'TreatmentCondition',
        'SeriousIllness', 'SurgicalOperation', 'Hospitalized', 'HospitalizationDetails',
        'PrescriptionMedication', 'NonPrescriptionMedication', 'TobaccoUse', 'AlcoholDrugUse',
        'AllergicLocalAnesthetic', 'AllergicPenicillin', 'AllergicAntibiotics', 'AllergicSulfaDrugs',
        'AllergicAspirin', 'AllergicLatex', 'AllergicOthers', 'BleedingTime', 'Pregnant',
        'Nursing', 'BirthPills', 'BloodType', 'BloodPressure', 'CreatedDate'
    ]
    
    existing_columns = [column[1] for column in columns]
    
    print("\nColumn verification:")
    print("-" * 50)
    for required_col in required_columns:
        if required_col in existing_columns:
            print(f"✓ {required_col}")
        else:
            print(f"✗ {required_col} - MISSING")
    
    # Check Appointments table
    cursor.execute("PRAGMA table_info(Appointments)")
    appointment_columns = cursor.fetchall()
    
    print("\nAppointments table columns:")
    print("-" * 50)
    for column in appointment_columns:
        print(f"{column[1]} ({column[2]})")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM Patients")
    patient_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Appointments")
    appointment_count = cursor.fetchone()[0]
    
    print(f"\nDatabase statistics:")
    print("-" * 50)
    print(f"Patients: {patient_count}")
    print(f"Appointments: {appointment_count}")
    
    conn.close()

if __name__ == "__main__":
    check_database() 