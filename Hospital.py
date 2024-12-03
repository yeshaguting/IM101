import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="hospital_db"
)

cursor = db.cursor()

# Create Tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    age INT,
    gender VARCHAR(10),
    admission_date DATE,
    room VARCHAR(100),
    diagnosis VARCHAR(255),
    `status` VARCHAR(200)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    department VARCHAR(255)
)
""")

db.commit()

# User Interface
root = tk.Tk()
root.title("Hospital Patient Information System")
root.geometry("1200x700")  # Window Size
root.config(bg="#f9f9f9")  # Background Color

# Utility Functions
def clear_patient_fields():
    patient_name.delete(0, tk.END)
    patient_age.delete(0, tk.END)
    patient_gender.set('')
    patient_room.delete(0, tk.END)
    patient_diagnosis.delete(0, tk.END)
    patient_status.set('')

def clear_doctor_fields():
    doctor_name.delete(0, tk.END)
    doctor_department.delete(0, tk.END)

def load_patients():
    for row in patient_table.get_children():
        patient_table.delete(row)
    cursor.execute("SELECT * FROM patients")
    for patient in cursor.fetchall():
        patient_table.insert("", "end", values=patient)

def load_doctors():
    for row in doctor_table.get_children():
        doctor_table.delete(row)
    cursor.execute("SELECT * FROM doctors")
    for doctor in cursor.fetchall():
        doctor_table.insert("", "end", values=doctor)

def load_rooms():
    for row in room_table.get_children():
        room_table.delete(row)
    cursor.execute("SELECT room, name, admission_date FROM patients WHERE status != 'Discharged'")
    for room in cursor.fetchall():
        room_table.insert("", "end", values=room)

def display_selected_patient(event):
    clear_patient_fields()
    selected = patient_table.focus()
    values = patient_table.item(selected, 'values')

    if values:
        patient_name.insert(0, values[1])
        patient_age.insert(0, values[2])
        patient_gender.set(values[3])
        patient_room.insert(0, values[5])
        patient_diagnosis.insert(0, values[6])
        patient_status.set(values[7])

def display_selected_doctor(event):
    clear_doctor_fields()
    selected = doctor_table.focus()
    values = doctor_table.item(selected, 'values')

    if values:
        doctor_name.insert(0, values[1])
        doctor_department.insert(0, values[2])

def add_patient():
    name, age, gender, room, diagnosis, status = (
        patient_name.get(),
        patient_age.get(),
        patient_gender.get(),
        patient_room.get(),
        patient_diagnosis.get(),
        patient_status.get()
    )

    if name and age and gender and room and diagnosis and status:
        cursor.execute("""
            INSERT INTO patients (name, age, gender, admission_date, room, diagnosis, status)
            VALUES (%s, %s, %s, CURDATE(), %s, %s, %s)
        """, (name, age, gender, room, diagnosis, status))
        db.commit()
        load_patients()
        load_rooms()  # Update room view
        messagebox.showinfo("Success", "Patient added successfully!")
        clear_patient_fields()
    else:
        messagebox.showwarning("Input Error", "All fields are required.")

def update_patient():
    selected = patient_table.focus()
    values = patient_table.item(selected, 'values')

    if not values:
        messagebox.showwarning("Selection Error", "Please select a patient to update.")
        return

    id = values[0]
    name, age, gender, room, diagnosis, status = (
        patient_name.get(),
        patient_age.get(),
        patient_gender.get(),
        patient_room.get(),
        patient_diagnosis.get(),
        patient_status.get()
    )

    if name and age and gender and room and diagnosis and status:
        cursor.execute("""
            UPDATE patients SET name=%s, age=%s, gender=%s, room=%s, diagnosis=%s, status=%s WHERE id=%s
        """, (name, age, gender, room, diagnosis, status, id))
        db.commit()
        load_patients()
        load_rooms()  # Update room view
        messagebox.showinfo("Success", "Patient updated successfully!")
        clear_patient_fields()
    else:
        messagebox.showwarning("Input Error", "All fields are required.")

def delete_patient():
    selected = patient_table.focus()
    values = patient_table.item(selected, 'values')

    if not values:
        messagebox.showwarning("Selection Error", "Please select a patient to delete.")
        return

    cursor.execute("DELETE FROM patients WHERE id=%s", (values[0],))
    db.commit()
    load_patients()
    load_rooms()  # Update room view
    messagebox.showinfo("Success", "Patient deleted successfully!")
    clear_patient_fields()

def add_doctor():
    name, department = (
        doctor_name.get(),
        doctor_department.get()
    )

    if name and department:
        cursor.execute("""
            INSERT INTO doctors (name, department)
            VALUES (%s, %s)
        """, (name, department))
        db.commit()
        load_doctors()
        messagebox.showinfo("Success", "Doctor added successfully!")
        clear_doctor_fields()
    else:
        messagebox.showwarning("Input Error", "All fields are required.")

def update_doctor():
    selected = doctor_table.focus()
    values = doctor_table.item(selected, 'values')

    if not values:
        messagebox.showwarning("Selection Error", "Please select a doctor to update.")
        return

    id = values[0]
    name, department = (
        doctor_name.get(),
        doctor_department.get()
    )

    if name and department:
        cursor.execute("""
            UPDATE doctors SET name=%s, department=%s WHERE id=%s
        """, (name, department, id))
        db.commit()
        load_doctors()
        messagebox.showinfo("Success", "Doctor updated successfully!")
        clear_doctor_fields()
    else:
        messagebox.showwarning("Input Error", "All fields are required.")

def delete_doctor():
    selected = doctor_table.focus()
    values = doctor_table.item(selected, 'values')

    if not values:
        messagebox.showwarning("Selection Error", "Please select a doctor to delete.")
        return

    cursor.execute("DELETE FROM doctors WHERE id=%s", (values[0],))
    db.commit()
    load_doctors()
    messagebox.showinfo("Success", "Doctor deleted successfully!")
    clear_doctor_fields()


def search():
    query = search_entry.get().strip()

    # Clear the previous results
    for row in patient_table.get_children():
        patient_table.delete(row)
    for row in doctor_table.get_children():
        doctor_table.delete(row)
    for row in room_table.get_children():
        room_table.delete(row)

    # Search patients
    if query:
        cursor.execute("SELECT * FROM patients WHERE name LIKE %s", (f"%{query}%",))
        patient_rows = cursor.fetchall()
        for patient in patient_rows:
            patient_table.insert("", "end", values=patient)

        # Search doctors
        cursor.execute("SELECT * FROM doctors WHERE name LIKE %s", (f"%{query}%",))
        doctor_rows = cursor.fetchall()
        for doctor in doctor_rows:
            doctor_table.insert("", "end", values=doctor)

        # Search rooms
        cursor.execute("""
            SELECT room, name, admission_date 
            FROM patients 
            WHERE room LIKE %s OR name LIKE %s
            """, (f"%{query}%", f"%{query}%"))
        room_rows = cursor.fetchall()
        for room in room_rows:
            room_table.insert("", "end", values=room)

def switch_tab(event):
    selected_tab = notebook.tab(notebook.select(), "text")
    if selected_tab == "Patients":
        load_patients()
        clear_patient_fields()  # Clear fields when switching tabs
    elif selected_tab == "Doctors":
        load_doctors()
        clear_doctor_fields()  # Clear fields when switching tabs
    elif selected_tab == "View Rooms":
        load_rooms()  # Load room data when switching to View Rooms tab

# Dashboard
dashboard_frame = tk.Frame(root, bg="#ffffff")
dashboard_frame.pack(fill="both", expand=True)

# Navigation Bar Frame
navbar = tk.Frame(dashboard_frame, bg="#BAE0F3", height=20)
navbar.pack(side="top", fill="x")

tk.Label(navbar, text="Dashboard", font=("Helvetica", 26, "bold"), bg="#BAE0F3").pack(pady=10)

# Patient Input Fields
input_frame = tk.Frame(navbar, bg="#BAE0F3")
input_frame.pack(pady=10)

tk.Label(input_frame, text="Patient Name:", bg="#BAE0F3").grid(row=0, column=0, padx=5, pady=5, sticky='w')
patient_name = ttk.Entry(input_frame, width=25)
patient_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Age:", bg="#BAE0F3").grid(row=1, column=0, padx=5, pady=5, sticky='w')
patient_age = ttk.Entry(input_frame, width=25)
patient_age.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Gender:", bg="#BAE0F3").grid(row=2, column=0, padx=5, pady=5, sticky='w')
patient_gender = ttk.Combobox(input_frame, values=["Male", "Female"], width=23)
patient_gender.grid(row=2, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Room:", bg="#BAE0F3").grid(row=3, column=0, padx=5, pady=5, sticky='w')
patient_room = ttk.Entry(input_frame, width=25)
patient_room.grid(row=3, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Diagnosis:", bg="#BAE0F3").grid(row=0, column=2, padx=5, pady=5, sticky='w')
patient_diagnosis = ttk.Entry(input_frame, width=25)
patient_diagnosis.grid(row=0, column=3, padx=5, pady=5)

tk.Label(input_frame, text="Status:", bg="#BAE0F3").grid(row=1, column=2, padx=5, pady=5, sticky='w')
patient_status = ttk.Combobox(input_frame, values=["Discharged", "Exp. Hospital Stay", "Ext. Hospitalization", "Surgery", "In Surgery", "Unavailable"], width=23)
patient_status.grid(row=1, column=3, padx=5, pady=5)

# Divider
divider = tk.Frame(navbar, bg="#FFFFFF", height=1)
divider.pack(fill="x", padx=20, pady=10)

# Doctor Input Fields
doctor_input_frame = tk.Frame(navbar, bg="#BAE0F3")
doctor_input_frame.pack(pady=10)

tk.Label(doctor_input_frame, text="Doctor Name:", bg="#BAE0F3").grid(row=0, column=0, padx=5, pady=5, sticky='w')
doctor_name = ttk.Entry(doctor_input_frame, width=25)
doctor_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(doctor_input_frame, text="Department:", bg="#BAE0F3").grid(row=1, column=0, padx=5, pady=5, sticky='w')
doctor_department = ttk.Entry(doctor_input_frame, width=25)
doctor_department.grid(row=1, column=1, padx=5, pady=5)

# Divider
divider = tk.Frame(navbar, bg="#FFFFFF", height=1)
divider.pack(fill="x", padx=20, pady=10)

# Buttons
buttons_frame = tk.Frame(navbar, bg="#BAE0F3")
buttons_frame.pack(pady=10)

ttk.Button(buttons_frame, text="Add Patient", command=add_patient).grid(row=0, column=0, padx=10)
ttk.Button(buttons_frame, text="Update Patient", command=update_patient).grid(row=0, column=1, padx=10)
ttk.Button(buttons_frame, text="Delete Patient", command=delete_patient).grid(row=0, column=2, padx=10)
ttk.Button(buttons_frame, text="Clear Patient Fields", command=clear_patient_fields).grid(row=0, column=3, padx=10)

ttk.Button(buttons_frame, text="Add Doctor", command=add_doctor).grid(row=1, column=0, padx=10)
ttk.Button(buttons_frame, text="Update Doctor", command=update_doctor).grid(row=1, column=1, padx=10)
ttk.Button(buttons_frame, text="Delete Doctor", command=delete_doctor).grid(row=1, column=2, padx=10)
ttk.Button(buttons_frame, text="Clear Doctor Fields", command=clear_doctor_fields).grid(row=1, column=3, padx=10)

# Right Side: Search Bar
search_frame = tk.Frame(navbar, bg="#BAE0F3")
search_frame.pack(side="right", padx=20, pady=10)

search_entry = ttk.Entry(search_frame, width=30)
search_entry.grid(row=0, column=0, padx=5)
ttk.Button(search_frame, text="Search", command=search).grid(row=0, column=1, padx=5)

# Navigation
notebook = ttk.Notebook(dashboard_frame)
patients_tab = ttk.Frame(notebook)
doctors_tab = ttk.Frame(notebook)
rooms_tab = ttk.Frame(notebook)

notebook.add(patients_tab, text="Patients")
notebook.add(doctors_tab, text="Doctors")
notebook.add(rooms_tab, text="View Rooms")
notebook.pack(expand=True, fill="both")

# Patient Tab
columns = ("ID", "Name", "Age", "Gender", "Admission Date", "Room", "Diagnosis", "Status")
patient_table = ttk.Treeview(patients_tab, columns=columns, show="headings", height=20)

for col in columns:
    patient_table.heading(col, text=col)
    patient_table.column(col, anchor='center', width=120)

patient_table.bind("<<TreeviewSelect>>", display_selected_patient)  # Bind row selection event
patient_table.pack(fill="both", expand=True, padx=20, pady=10)

# Doctors Tab
columns = ("ID", "Name", "Department")
doctor_table = ttk.Treeview(doctors_tab, columns=columns, show="headings", height=20)

for col in columns:
    doctor_table.heading(col, text=col)
    doctor_table.column(col, anchor='center', width=120)

doctor_table.bind("<<TreeviewSelect>>", display_selected_doctor)  # Bind row selection event
doctor_table.pack(fill="both", expand=True, padx=20, pady=10)

# View Rooms Tab
columns = ("Room", "Patient Name", "Admission Date")
room_table = ttk.Treeview(rooms_tab, columns=columns, show="headings", height=20)

for col in columns:
    room_table.heading(col, text=col)
    room_table.column(col, anchor='center', width=120)

room_table.pack(fill="both", expand=True, padx=20, pady=10)

# Style for Table
style = ttk.Style()
style.theme_use("clam")  # Modern theme
style.configure(
    "Treeview",
    background="#ffffff",      # White background
    foreground="#000000",      # Black text
    rowheight=30,              # Increase row height for better spacing
    fieldbackground="#ffffff"  # White field background
)
style.map("Treeview", background=[("selected", "#BAE0F3")])  # Highlight color on selection

# Style for Table Header
style.configure(
    "Treeview.Heading",
    background="#BAE0F3",      # Light blue header background
    foreground="#333333",      # Darker header text
    font=("Helvetica", 12, "bold"),  # Bold font for headers
    relief="flat"              # Flat header style
)
style.map(
    "Treeview.Heading",
    background=[("active", "#a9d5e8")]  # Slightly darker blue on hover
)

# Configure Notebook Tabs
style.configure(
    "TNotebook",
    background="#FFFFFF",  # Notebook background
    borderwidth=0,
)

style.configure(
    "TNotebook.Tab",
    background="#12086F",  # Tab background
    foreground="#FFFFFF",  # Tab text color
    font=("Helvetica", 12, "bold"),  # Tab font
    padding=(10, 5),  # Padding inside tabs
)

style.map(
    "TNotebook.Tab",
    background=[("selected", "#FFFFFF")],  # Active tab background
    foreground=[("selected", "#000000")],  # Active tab text color
)

# Create a style for buttons
style.configure("TButton",
                background="#12086F",  # Set button background color
                foreground="white",     # Set button text color
                font=("Helvetica", 10, "bold"))  # Set font

# Optional: Change hover effect
style.map("TButton",
          background=[('active', '#2B35AF')],  # Color when hovered
          foreground=[('active', 'white')])     # Text color when hovered

# Load initial data
load_patients()
load_doctors()
load_rooms()  # Load room data initially

# Bind tab change event
notebook.bind("<<NotebookTabChanged>>", switch_tab)

root.mainloop()