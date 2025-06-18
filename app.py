from flask import Flask, render_template, request, redirect, jsonify, url_for
import sqlite3
import os
from datetime import datetime, date
import calendar

app = Flask(__name__)

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
    
    # Create Patients table
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
        
        # Validate required fields
        if not name or not contact:
            return render_template('create_patient.html', 
                                 error_message="Name and Contact are required fields.")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Patients (Name, Contact, Email, DateOfBirth, Address, EmergencyContact, MedicalHistory)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, contact, email, date_of_birth, address, emergency_contact, medical_history))
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
        
        # Validate required fields
        if not name or not contact:
            cursor.execute("SELECT * FROM Patients WHERE ID = ?", (patient_id,))
            patient = cursor.fetchone()
            conn.close()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Name and Contact are required fields.'}), 400
            
            return render_template('edit_patient.html', 
                                 patient=patient, 
                                 error_message="Name and Contact are required fields.")
        
        try:
            cursor.execute("""
                UPDATE Patients 
                SET Name = ?, Contact = ?, Email = ?, DateOfBirth = ?, 
                    Address = ?, EmergencyContact = ?, MedicalHistory = ?
                WHERE ID = ?
            """, (name, contact, email, date_of_birth, address, emergency_contact, medical_history, patient_id))
            conn.commit()
            conn.close()
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Patient updated successfully'})
            
            return redirect('/patients')
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
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if selected_date and dental_care_filter:
        cursor.execute("SELECT * FROM Appointments WHERE Date = ? AND DentalCare LIKE ?", 
                      (selected_date, f'%{dental_care_filter}%'))
    elif selected_date:
        cursor.execute("SELECT * FROM Appointments WHERE Date = ?", (selected_date,))
    elif dental_care_filter:
        cursor.execute("SELECT * FROM Appointments WHERE DentalCare LIKE ?", (f'%{dental_care_filter}%',))
    else:
        cursor.execute("SELECT * FROM Appointments ORDER BY Date, Time")
    
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
                         current_datetime=current_datetime)

@app.route('/edit/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    if request.method == 'POST':
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

if __name__ == '__main__':
    app.run(debug=True)
