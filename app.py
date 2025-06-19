from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
import sqlite3
import os
from datetime import datetime, date
import calendar
import json

app = Flask(__name__)
app.secret_key = "your-very-secret-key"

# Jinja filter for 12-hour time format
@app.template_filter('ampm')
def ampm_filter(value):
    try:
        # Try parsing as HH:MM (24-hour)
        t = datetime.strptime(value, "%H:%M")
        return t.strftime("%I:%M %p").lstrip('0')
    except Exception:
        return value  # fallback if parsing fails

# SQLite DB path
DB_FILE = "dental.db"

def init_db():
    """Initialize the database with the required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create Patients table with additional fields
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
            Religion TEXT,
            HomeAddress TEXT,
            Occupation TEXT,
            DentalInsurance TEXT,
            EffectiveDate TEXT,
            ParentGuardianName TEXT,
            ParentGuardianOccupation TEXT,
            ReferralSource TEXT,
            ConsultationReason TEXT,
            DentalHistory TEXT,
            PreviousDentist TEXT,
            LastDentalVisit TEXT,
            Sex TEXT,
            Nickname TEXT,
            Age TEXT,
            Nationality TEXT,
            GoodHealth TEXT,
            MedicalTreatment TEXT,
            TreatmentCondition TEXT,
            SeriousIllness TEXT,
            SurgicalOperation TEXT,
            Hospitalized TEXT,
            HospitalizationDetails TEXT,
            PrescriptionMedication TEXT,
            NonPrescriptionMedication TEXT,
            TobaccoUse TEXT,
            AlcoholDrugUse TEXT,
            AllergicLocalAnesthetic TEXT,
            AllergicPenicillin TEXT,
            AllergicAntibiotics TEXT,
            AllergicSulfaDrugs TEXT,
            AllergicAspirin TEXT,
            AllergicLatex TEXT,
            AllergicOthers TEXT,
            BleedingTime TEXT,
            Pregnant TEXT,
            Nursing TEXT,
            BirthPills TEXT,
            BloodType TEXT,
            BloodPressure TEXT,
            CreatedDate TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Appointments (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PatientName TEXT NOT NULL,
            Contact TEXT NOT NULL,
            Date TEXT NOT NULL,
            Time TEXT NOT NULL,
            DentalCare TEXT NOT NULL
        )
    ''')
    
    # Create DentalCharts table for intraoral examination
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

def validate_appointment_date(appointment_date, appointment_id=None):
    """Validate that appointment date is not in the past"""
    try:
        # Parse the appointment date
        app_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        today = date.today()
        
        # For editing, allow the current appointment date
        if appointment_id:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT Date FROM Appointments WHERE ID = ?", (appointment_id,))
            current_date = cursor.fetchone()
            conn.close()
            
            if current_date and current_date[0] == appointment_date:
                return True, None  # Allow keeping the same date
        
        # Check if date is in the past
        if app_date < today:
            return False, "Appointment date cannot be in the past. Please select a current or future date."
        
        return True, None
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD format."

def check_appointment_conflict(appointment_date, appointment_time, appointment_id=None):
    """Check if there's already an appointment at the same date and time"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if appointment_id:
        # For editing, exclude the current appointment from the check
        cursor.execute("""
            SELECT COUNT(*) FROM Appointments 
            WHERE Date = ? AND Time = ? AND ID != ?
        """, (appointment_date, appointment_time, appointment_id))
    else:
        # For new appointments, check all appointments at that date/time
        cursor.execute("""
            SELECT COUNT(*) FROM Appointments 
            WHERE Date = ? AND Time = ?
        """, (appointment_date, appointment_time))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    if count > 0:
        return False, f"There is already an appointment scheduled for {appointment_date} at {appointment_time}. Please choose a different date or time."
    
    return True, None

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-patient', methods=['GET', 'POST'])
def create_patient():
    """Create a new patient"""
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        email = request.form.get('email', '')
        date_of_birth = request.form.get('date_of_birth', '')
        address = request.form.get('address', '')
        emergency_contact = request.form.get('emergency_contact', '')
        medical_history = request.form.get('medical_history', '')
        religion = request.form.get('religion', '')
        home_address = request.form.get('home_address', '')
        occupation = request.form.get('occupation', '')
        dental_insurance = request.form.get('dental_insurance', '')
        effective_date = request.form.get('effective_date', '')
        parent_guardian_name = request.form.get('parent_guardian_name', '')
        parent_guardian_occupation = request.form.get('parent_guardian_occupation', '')
        referral_source = request.form.get('referral_source', '')
        consultation_reason = request.form.get('consultation_reason', '')
        dental_history = request.form.get('dental_history', '')
        previous_dentist = request.form.get('previous_dentist', '')
        last_dental_visit = request.form.get('last_dental_visit', '')
        sex = request.form.get('sex', '')
        nickname = request.form.get('nickname', '')
        age = request.form.get('age', '')
        nationality = request.form.get('nationality', '')
        
        # Medical History Fields
        good_health = request.form.get('good_health', '')
        medical_treatment = request.form.get('medical_treatment', '')
        treatment_condition = request.form.get('treatment_condition', '')
        serious_illness = request.form.get('serious_illness', '')
        surgical_operation = request.form.get('surgical_operation', '')
        hospitalized = request.form.get('hospitalized', '')
        hospitalization_details = request.form.get('hospitalization_details', '')
        prescription_medication = request.form.get('prescription_medication', '')
        non_prescription_medication = request.form.get('non_prescription_medication', '')
        tobacco_use = request.form.get('tobacco_use', '')
        alcohol_drug_use = request.form.get('alcohol_drug_use', '')
        allergic_local_anesthetic = request.form.get('allergic_local_anesthetic', '')
        allergic_penicillin = request.form.get('allergic_penicillin', '')
        allergic_antibiotics = request.form.get('allergic_antibiotics', '')
        allergic_sulfa_drugs = request.form.get('allergic_sulfa_drugs', '')
        allergic_aspirin = request.form.get('allergic_aspirin', '')
        allergic_latex = request.form.get('allergic_latex', '')
        allergic_others = request.form.get('allergic_others', '')
        bleeding_time = request.form.get('bleeding_time', '')
        pregnant = request.form.get('pregnant', '')
        nursing = request.form.get('nursing', '')
        birth_pills = request.form.get('birth_pills', '')
        blood_type = request.form.get('blood_type', '')
        blood_pressure = request.form.get('blood_pressure', '')
        
        # Validate required fields
        if not name or not contact:
            return render_template('create_patient.html', 
                                 error_message="Name and Contact are required fields.")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Patients (Name, Contact, Email, DateOfBirth, Address, EmergencyContact, MedicalHistory,
                                    Religion, HomeAddress, Occupation, DentalInsurance, EffectiveDate,
                                    ParentGuardianName, ParentGuardianOccupation, ReferralSource, ConsultationReason,
                                    DentalHistory, PreviousDentist, LastDentalVisit, Sex, Nickname, Age, Nationality,
                                    GoodHealth, MedicalTreatment, TreatmentCondition, SeriousIllness, SurgicalOperation,
                                    Hospitalized, HospitalizationDetails, PrescriptionMedication, NonPrescriptionMedication,
                                    TobaccoUse, AlcoholDrugUse, AllergicLocalAnesthetic, AllergicPenicillin, AllergicAntibiotics,
                                    AllergicSulfaDrugs, AllergicAspirin, AllergicLatex, AllergicOthers, BleedingTime,
                                    Pregnant, Nursing, BirthPills, BloodType, BloodPressure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, contact, email, date_of_birth, address, emergency_contact, medical_history,
                  religion, home_address, occupation, dental_insurance, effective_date,
                  parent_guardian_name, parent_guardian_occupation, referral_source, consultation_reason,
                  dental_history, previous_dentist, last_dental_visit, sex, nickname, age, nationality,
                  good_health, medical_treatment, treatment_condition, serious_illness, surgical_operation,
                  hospitalized, hospitalization_details, prescription_medication, non_prescription_medication,
                  tobacco_use, alcohol_drug_use, allergic_local_anesthetic, allergic_penicillin, allergic_antibiotics,
                  allergic_sulfa_drugs, allergic_aspirin, allergic_latex, allergic_others, bleeding_time,
                  pregnant, nursing, birth_pills, blood_type, blood_pressure))
            conn.commit()
            conn.close()
            
            return redirect('/patients')
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('create_patient.html', 
                                 error_message="A patient with this name already exists.")
    
    return render_template('create_patient.html')

@app.route('/edit-patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    """Edit an existing patient"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        email = request.form.get('email', '')
        date_of_birth = request.form.get('date_of_birth', '')
        address = request.form.get('address', '')
        emergency_contact = request.form.get('emergency_contact', '')
        medical_history = request.form.get('medical_history', '')
        religion = request.form.get('religion', '')
        home_address = request.form.get('home_address', '')
        occupation = request.form.get('occupation', '')
        dental_insurance = request.form.get('dental_insurance', '')
        effective_date = request.form.get('effective_date', '')
        parent_guardian_name = request.form.get('parent_guardian_name', '')
        parent_guardian_occupation = request.form.get('parent_guardian_occupation', '')
        referral_source = request.form.get('referral_source', '')
        consultation_reason = request.form.get('consultation_reason', '')
        dental_history = request.form.get('dental_history', '')
        previous_dentist = request.form.get('previous_dentist', '')
        last_dental_visit = request.form.get('last_dental_visit', '')
        sex = request.form.get('sex', '')
        nickname = request.form.get('nickname', '')
        age = request.form.get('age', '')
        nationality = request.form.get('nationality', '')
        
        # Medical History Fields
        good_health = request.form.get('good_health', '')
        medical_treatment = request.form.get('medical_treatment', '')
        treatment_condition = request.form.get('treatment_condition', '')
        serious_illness = request.form.get('serious_illness', '')
        surgical_operation = request.form.get('surgical_operation', '')
        hospitalized = request.form.get('hospitalized', '')
        hospitalization_details = request.form.get('hospitalization_details', '')
        prescription_medication = request.form.get('prescription_medication', '')
        non_prescription_medication = request.form.get('non_prescription_medication', '')
        tobacco_use = request.form.get('tobacco_use', '')
        alcohol_drug_use = request.form.get('alcohol_drug_use', '')
        allergic_local_anesthetic = request.form.get('allergic_local_anesthetic', '')
        allergic_penicillin = request.form.get('allergic_penicillin', '')
        allergic_antibiotics = request.form.get('allergic_antibiotics', '')
        allergic_sulfa_drugs = request.form.get('allergic_sulfa_drugs', '')
        allergic_aspirin = request.form.get('allergic_aspirin', '')
        allergic_latex = request.form.get('allergic_latex', '')
        allergic_others = request.form.get('allergic_others', '')
        bleeding_time = request.form.get('bleeding_time', '')
        pregnant = request.form.get('pregnant', '')
        nursing = request.form.get('nursing', '')
        birth_pills = request.form.get('birth_pills', '')
        blood_type = request.form.get('blood_type', '')
        blood_pressure = request.form.get('blood_pressure', '')
        
        # Validate required fields
        if not name or not contact:
            cursor.execute("SELECT * FROM Patients WHERE ID = ?", (patient_id,))
            patient = cursor.fetchone()
            conn.close()
            
            # Create specific error messages
            error_messages = []
            if not name:
                error_messages.append("Patient name is required")
            if not contact:
                error_messages.append("Contact number is required")
            
            error_message = " and ".join(error_messages) + "."
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': error_message}), 400
            
            return render_template('edit_patient.html', 
                                 patient=patient, 
                                 error_message=error_message)
        
        # Additional validation for email if provided
        if email and not email.strip():
            email = ''  # Convert empty string to None for database
        elif email:
            import re
            email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
            if not email_pattern.match(email):
                cursor.execute("SELECT * FROM Patients WHERE ID = ?", (patient_id,))
                patient = cursor.fetchone()
                conn.close()
                
                error_message = "Please provide a valid email address."
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': error_message}), 400
                
                return render_template('edit_patient.html', 
                                     patient=patient, 
                                     error_message=error_message)
        
        try:
            cursor.execute("""
                UPDATE Patients 
                SET Name = ?, Contact = ?, Email = ?, DateOfBirth = ?, 
                    Address = ?, EmergencyContact = ?, MedicalHistory = ?,
                    Religion = ?, HomeAddress = ?, Occupation = ?, DentalInsurance = ?, EffectiveDate = ?,
                    ParentGuardianName = ?, ParentGuardianOccupation = ?, ReferralSource = ?, ConsultationReason = ?,
                    DentalHistory = ?, PreviousDentist = ?, LastDentalVisit = ?, Sex = ?, Nickname = ?, Age = ?, Nationality = ?,
                    GoodHealth = ?, MedicalTreatment = ?, TreatmentCondition = ?, SeriousIllness = ?, SurgicalOperation = ?,
                    Hospitalized = ?, HospitalizationDetails = ?, PrescriptionMedication = ?, NonPrescriptionMedication = ?,
                    TobaccoUse = ?, AlcoholDrugUse = ?, AllergicLocalAnesthetic = ?, AllergicPenicillin = ?, AllergicAntibiotics = ?,
                    AllergicSulfaDrugs = ?, AllergicAspirin = ?, AllergicLatex = ?, AllergicOthers = ?, BleedingTime = ?,
                    Pregnant = ?, Nursing = ?, BirthPills = ?, BloodType = ?, BloodPressure = ?
                WHERE ID = ?
            """, (name, contact, email, date_of_birth, address, emergency_contact, medical_history,
                  religion, home_address, occupation, dental_insurance, effective_date,
                  parent_guardian_name, parent_guardian_occupation, referral_source, consultation_reason,
                  dental_history, previous_dentist, last_dental_visit, sex, nickname, age, nationality,
                  good_health, medical_treatment, treatment_condition, serious_illness, surgical_operation,
                  hospitalized, hospitalization_details, prescription_medication, non_prescription_medication,
                  tobacco_use, alcohol_drug_use, allergic_local_anesthetic, allergic_penicillin, allergic_antibiotics,
                  allergic_sulfa_drugs, allergic_aspirin, allergic_latex, allergic_others, bleeding_time,
                  pregnant, nursing, birth_pills, blood_type, blood_pressure, patient_id))
            conn.commit()
            conn.close()
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Patient updated successfully'})
            
            return redirect('/patients?success=patient_updated')
        except sqlite3.IntegrityError:
            conn.close()
            cursor.execute("SELECT * FROM Patients WHERE ID = ?", (patient_id,))
            patient = cursor.fetchone()
            
            error_msg = "A patient with this name already exists."
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': error_msg}), 400
            
            return render_template('edit_patient.html', 
                                 patient=patient, 
                                 error_message=error_msg)
    
    # GET request - show edit form
    cursor.execute("SELECT * FROM Patients WHERE ID = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    
    if patient is None:
        return redirect('/patients')
    
    return render_template('edit_patient.html', patient=patient)

@app.route('/delete-patient/<int:patient_id>')
def delete_patient(patient_id):
    """Delete a patient and all their appointments"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get patient name before deletion
    cursor.execute("SELECT Name FROM Patients WHERE ID = ?", (patient_id,))
    patient = cursor.fetchone()
    
    if patient:
        patient_name = patient[0]
        # Delete all appointments for this patient
        cursor.execute("DELETE FROM Appointments WHERE PatientName = ?", (patient_name,))
        # Delete the patient
        cursor.execute("DELETE FROM Patients WHERE ID = ?", (patient_id,))
        conn.commit()
    
    conn.close()
    return redirect('/patients')

@app.route('/patients')
def patients():
    """Show list of all patients with their appointment counts"""
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))  # Default 10 records per page
    
    # Validate page and per_page parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:  # Limit to reasonable range
        per_page = 10
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get total count for pagination
    if search_query:
        cursor.execute("""
            SELECT COUNT(DISTINCT p.ID)
            FROM Patients p
            LEFT JOIN Appointments a ON p.Name = a.PatientName
            WHERE p.Name LIKE ?
        """, (f'%{search_query}%',))
    else:
        cursor.execute("SELECT COUNT(*) FROM Patients")
    
    total_patients = cursor.fetchone()[0]
    
    # Calculate pagination
    total_pages = (total_patients + per_page - 1) // per_page
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    offset = (page - 1) * per_page
    
    # Get patients with pagination
    if search_query:
        cursor.execute("""
            SELECT p.ID, p.Name, p.Contact, p.Email, p.DateOfBirth, p.CreatedDate,
                   COUNT(a.ID) as appointment_count,
                   MIN(a.Date) as first_appointment, MAX(a.Date) as last_appointment
            FROM Patients p
            LEFT JOIN Appointments a ON p.Name = a.PatientName
            WHERE p.Name LIKE ?
            GROUP BY p.ID, p.Name, p.Contact, p.Email, p.DateOfBirth, p.CreatedDate
            ORDER BY p.Name
            LIMIT ? OFFSET ?
        """, (f'%{search_query}%', per_page, offset))
    else:
        cursor.execute("""
            SELECT p.ID, p.Name, p.Contact, p.Email, p.DateOfBirth, p.CreatedDate,
                   COUNT(a.ID) as appointment_count,
                   MIN(a.Date) as first_appointment, MAX(a.Date) as last_appointment
            FROM Patients p
            LEFT JOIN Appointments a ON p.Name = a.PatientName
            GROUP BY p.ID, p.Name, p.Contact, p.Email, p.DateOfBirth, p.CreatedDate
            ORDER BY p.Name
            LIMIT ? OFFSET ?
        """, (per_page, offset))
    
    patients = cursor.fetchall()
    conn.close()
    
    return render_template('patients.html', 
                         patients=patients, 
                         search_query=search_query,
                         page=page,
                         per_page=per_page,
                         total_patients=total_patients,
                         total_pages=total_pages)

@app.route('/patient/<patient_name>')
def patient_history(patient_name):
    """Show detailed appointment history for a specific patient"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get patient details
    cursor.execute("SELECT * FROM Patients WHERE Name = ?", (patient_name,))
    patient = cursor.fetchone()
    
    if not patient:
        conn.close()
        return redirect('/patients')
    
    # Get all appointments for this patient
    cursor.execute("""
        SELECT * FROM Appointments 
        WHERE PatientName = ? 
        ORDER BY Date DESC, Time DESC
    """, (patient_name,))
    
    appointments = cursor.fetchall()
    
    # Get patient statistics
    if appointments:
        cursor.execute("""
            SELECT COUNT(*) as total_appointments,
                   MIN(Date) as first_appointment,
                   MAX(Date) as last_appointment,
                   COUNT(DISTINCT DentalCare) as unique_treatments
            FROM Appointments 
            WHERE PatientName = ?
        """, (patient_name,))
        
        stats = cursor.fetchone()
        
        # Get treatment history
        cursor.execute("""
            SELECT DentalCare, COUNT(*) as treatment_count
            FROM Appointments 
            WHERE PatientName = ?
            GROUP BY DentalCare
            ORDER BY treatment_count DESC
        """, (patient_name,))
        
        treatments = cursor.fetchall()
    else:
        stats = (0, None, None, 0)
        treatments = []
    
    conn.close()
    
    # Get current datetime for comparison
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    return render_template('patient_history.html', 
                         patient=patient,
                         patient_name=patient_name,
                         appointments=appointments,
                         stats=stats,
                         treatments=treatments,
                         current_datetime=current_datetime)

@app.route('/calendar')
def calendar_view():
    # Get current year and month, or from query parameters
    year = int(request.args.get('year', date.today().year))
    month = int(request.args.get('month', date.today().month))
    
    # Create calendar
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get appointments for the month
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get start and end dates for the month
    start_date = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1:04d}-01-01"
    else:
        end_date = f"{year:04d}-{month+1:02d}-01"
    
    cursor.execute("""
        SELECT * FROM Appointments 
        WHERE Date >= ? AND Date < ? 
        ORDER BY Date, Time
    """, (start_date, end_date))
    
    appointments = cursor.fetchall()
    conn.close()
    
    # Organize appointments by date
    appointments_by_date = {}
    total_appointments = 0
    for appointment in appointments:
        app_date = appointment[3]  # Date field
        if app_date not in appointments_by_date:
            appointments_by_date[app_date] = []
        appointments_by_date[app_date].append(appointment)
        total_appointments += 1
    
    # Calculate navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    # Get current datetime for comparison
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    return render_template('calendar.html', 
                         calendar=cal,
                         month_name=month_name,
                         year=year,
                         month=month,
                         appointments_by_date=appointments_by_date,
                         total_appointments=total_appointments,
                         prev_month=prev_month,
                         prev_year=prev_year,
                         next_month=next_month,
                         next_year=next_year,
                         current_datetime=current_datetime)

@app.route('/appointments')
def appointments():
    selected_date = request.args.get('date', '')
    dental_care_filter = request.args.get('dental_care', '')
    error_message = request.args.get('error', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 15))  # Default 15 records per page
    
    # Validate page and per_page parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:  # Limit to reasonable range
        per_page = 15
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Build the base query and count query
    base_conditions = []
    params = []
    
    if selected_date:
        base_conditions.append("Date = ?")
        params.append(selected_date)
    
    if dental_care_filter:
        base_conditions.append("DentalCare LIKE ?")
        params.append(f'%{dental_care_filter}%')
    
    where_clause = " AND ".join(base_conditions) if base_conditions else "1=1"
    
    # Get total count for pagination
    count_query = f"SELECT COUNT(*) FROM Appointments WHERE {where_clause}"
    cursor.execute(count_query, params)
    total_appointments = cursor.fetchone()[0]
    
    # Calculate pagination
    total_pages = (total_appointments + per_page - 1) // per_page
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    offset = (page - 1) * per_page
    
    # Get appointments with pagination
    query = f"SELECT * FROM Appointments WHERE {where_clause} ORDER BY Date, Time LIMIT ? OFFSET ?"
    cursor.execute(query, params + [per_page, offset])
    appointments = cursor.fetchall()
    
    # Get unique dental care types for filter dropdown
    cursor.execute("SELECT DISTINCT DentalCare FROM Appointments ORDER BY DentalCare")
    dental_care_types = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Set error message for past appointment editing
    if error_message == 'past_appointment':
        error_message = "Cannot edit appointments that have already passed."
    elif error_message == 'past_appointment_delete':
        error_message = "Cannot delete appointments that have already passed."
    
    # Get current datetime for comparison
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    return render_template('appointments.html', 
                         appointments=appointments, 
                         selected_date=selected_date,
                         dental_care_filter=dental_care_filter,
                         dental_care_types=dental_care_types,
                         error_message=error_message,
                         current_datetime=current_datetime,
                         page=page,
                         per_page=per_page,
                         total_appointments=total_appointments,
                         total_pages=total_pages)

@app.route('/edit/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    if request.method == 'POST':
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if is_ajax:
            # Handle AJAX request for modal
            name = request.form['name']
            contact = request.form['contact']
            appointment_date = request.form['date']
            time = request.form['time']
            dental_care = request.form['dental_care']

            # Validate appointment date
            is_valid, error_message = validate_appointment_date(appointment_date, appointment_id)
            if not is_valid:
                return jsonify({'success': False, 'error': error_message}), 400

            # Check for appointment conflicts (excluding current appointment)
            is_available, conflict_message = check_appointment_conflict(appointment_date, time, appointment_id)
            if not is_available:
                return jsonify({'success': False, 'error': conflict_message}), 400

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Appointments 
                SET PatientName = ?, Contact = ?, Date = ?, Time = ?, DentalCare = ?
                WHERE ID = ?
            """, (name, contact, appointment_date, time, dental_care, appointment_id))
            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': 'Appointment updated successfully'})
        else:
            # Handle regular form submission
            name = request.form['name']
            contact = request.form['contact']
            appointment_date = request.form['date']
            time = request.form['time']
            dental_care = request.form['dental_care']

            # Validate appointment date
            is_valid, error_message = validate_appointment_date(appointment_date, appointment_id)
            if not is_valid:
                # Get the appointment data to re-populate the form
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Appointments WHERE ID = ?", (appointment_id,))
                appointment = cursor.fetchone()
                conn.close()
                
                return render_template('edit_appointment.html', 
                                     appointment=appointment, 
                                     error_message=error_message)

            # Check for appointment conflicts (excluding current appointment)
            is_available, conflict_message = check_appointment_conflict(appointment_date, time, appointment_id)
            if not is_available:
                # Get the appointment data to re-populate the form
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Appointments WHERE ID = ?", (appointment_id,))
                appointment = cursor.fetchone()
                conn.close()
                
                return render_template('edit_appointment.html', 
                                     appointment=appointment, 
                                     error_message=conflict_message)

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Appointments 
                SET PatientName = ?, Contact = ?, Date = ?, Time = ?, DentalCare = ?
                WHERE ID = ?
            """, (name, contact, appointment_date, time, dental_care, appointment_id))
            conn.commit()
            conn.close()

            return redirect('/appointments')
    
    # GET request - show edit form
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Appointments WHERE ID = ?", (appointment_id,))
    appointment = cursor.fetchone()
    conn.close()
    
    if appointment is None:
        return redirect('/appointments')
    
    # Check if appointment has already passed
    appointment_datetime = f"{appointment[3]} {appointment[4]}"  # Date + Time
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    if appointment_datetime < current_datetime:
        # Redirect with error message
        return redirect('/appointments?error=past_appointment')
    
    return render_template('edit_appointment.html', appointment=appointment)

@app.route('/delete/<int:appointment_id>')
def delete_appointment(appointment_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # First, get the appointment details to check if it's in the past
    cursor.execute("SELECT * FROM Appointments WHERE ID = ?", (appointment_id,))
    appointment = cursor.fetchone()
    
    if appointment is None:
        conn.close()
        return redirect('/appointments')
    
    # Check if appointment has already passed
    appointment_datetime = f"{appointment[3]} {appointment[4]}"  # Date + Time
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    if appointment_datetime < current_datetime:
        conn.close()
        # Redirect with error message for past appointment deletion
        return redirect('/appointments?error=past_appointment_delete')
    
    # If appointment is not in the past, proceed with deletion
    cursor.execute("DELETE FROM Appointments WHERE ID = ?", (appointment_id,))
    conn.commit()
    conn.close()
    
    return redirect('/appointments')

@app.route('/api/appointments')
def api_appointments():
    selected_date = request.args.get('date', '')
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if selected_date:
        cursor.execute("SELECT * FROM Appointments WHERE Date = ? ORDER BY Time", (selected_date,))
    else:
        cursor.execute("SELECT * FROM Appointments ORDER BY Date, Time")
    
    appointments = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries for JSON response
    appointments_list = []
    for row in appointments:
        appointments_list.append({
            'id': row[0],
            'patient_name': row[1],
            'contact': row[2],
            'date': row[3],
            'time': row[4],
            'dental_care': row[5]
        })
    
    return jsonify(appointments_list)

@app.route('/api/appointment/<int:appointment_id>')
def api_appointment_details(appointment_id):
    """Get appointment details by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Appointments WHERE ID = ?", (appointment_id,))
    appointment = cursor.fetchone()
    conn.close()
    
    if appointment is None:
        return jsonify({'success': False, 'error': 'Appointment not found'}), 404
    
    appointment_data = {
        'id': appointment[0],
        'patient_name': appointment[1],
        'contact': appointment[2],
        'date': appointment[3],
        'time': appointment[4],
        'dental_care': appointment[5]
    }
    
    return jsonify({'success': True, 'appointment': appointment_data})

@app.route('/api/available-times')
def api_available_times():
    """Get available times for a specific date"""
    selected_date = request.args.get('date', '')
    
    if not selected_date:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get all booked times for the selected date
    cursor.execute("SELECT Time FROM Appointments WHERE Date = ? ORDER BY Time", (selected_date,))
    booked_times = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Generate all possible times (9 AM to 5 PM, 30-minute intervals)
    all_times = []
    for hour in range(9, 18):  # 9 AM to 5 PM
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            all_times.append(time_str)
    
    # Filter out booked times
    available_times = [time for time in all_times if time not in booked_times]
    
    return jsonify({
        'date': selected_date,
        'booked_times': booked_times,
        'available_times': available_times
    })

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        appointment_date = request.form['date']
        time = request.form['time']
        dental_care = request.form['dental_care']

        # Validate appointment date
        is_valid, error_message = validate_appointment_date(appointment_date)
        if not is_valid:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': error_message}), 400
            return render_template('add_appointment.html', 
                                 error_message=error_message,
                                 patient_name=name,
                                 contact=contact,
                                 date=appointment_date,
                                 time=time,
                                 dental_care=dental_care)

        # Check for appointment conflicts
        is_available, conflict_message = check_appointment_conflict(appointment_date, time)
        if not is_available:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': conflict_message}), 400
            return render_template('add_appointment.html', 
                                 error_message=conflict_message,
                                 patient_name=name,
                                 contact=contact,
                                 date=appointment_date,
                                 time=time,
                                 dental_care=dental_care)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Appointments (PatientName, Contact, Date, Time, DentalCare)
            VALUES (?, ?, ?, ?, ?)
        """, (name, contact, appointment_date, time, dental_care))
        conn.commit()
        conn.close()

        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Appointment created successfully'})
        
        return redirect('/appointments')
    
    # GET request - show form with optional pre-filled patient name
    patient_name = request.args.get('patient', '')
    return render_template('add_appointment.html', patient_name=patient_name)

@app.route('/patient/<patient_name>/treatment-records', methods=['GET', 'POST'])
def treatment_records(patient_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Get patient info
    cursor.execute("SELECT ID, Name FROM Patients WHERE Name = ?", (patient_name,))
    patient = cursor.fetchone()
    if not patient:
        conn.close()
        return redirect('/patients')
    patient_id = patient[0]
    error_message = None
    # Handle new record submission
    if request.method == 'POST':
        date_of_treatment = request.form['date_of_treatment']
        tooth_number = request.form.get('tooth_number', '')
        procedure = request.form.get('procedure', '')
        dentist_name = request.form.get('dentist_name', '')
        amount_charged = float(request.form.get('amount_charged', 0))
        amount_paid = float(request.form.get('amount_paid', 0))
        balance = amount_charged - amount_paid
        if not date_of_treatment:
            error_message = 'Date of treatment is required.'
        else:
            cursor.execute('''
                INSERT INTO TreatmentRecords
                (PatientID, DateOfTreatment, ToothNumber, Procedure, DentistName, AmountCharged, AmountPaid, Balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, date_of_treatment, tooth_number, procedure, dentist_name, amount_charged, amount_paid, balance))
            conn.commit()
            flash('Treatment record added successfully!', 'success')
    # Get all treatment records for this patient
    cursor.execute('''
        SELECT DateOfTreatment, ToothNumber, Procedure, DentistName, AmountCharged, AmountPaid, Balance
        FROM TreatmentRecords WHERE PatientID = ? ORDER BY DateOfTreatment DESC
    ''', (patient_id,))
    records = cursor.fetchall()
    conn.close()
    return render_template(
        'treatment_records.html',
        patient=patient,
        records=records,
        error_message=error_message,
        today=date.today().isoformat()
    )

if __name__ == '__main__':
    app.run(debug=True)
