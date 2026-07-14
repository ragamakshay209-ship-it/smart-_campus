import os
import json
import threading
from config import DATABASE_PATH

# Global lock to ensure thread safety across concurrent Streamlit sessions
db_lock = threading.Lock()

def get_file_path(filename):
    """Utility to get full file path in the database folder."""
    return os.path.join(DATABASE_PATH, filename)

def init_db():
    """Initializes all database files if they don't exist or are empty, seeding them with initial records."""
    import bcrypt
    
    def hash_pw(pw):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pw.encode('utf-8'), salt).decode('utf-8')
        
    default_schemas = {
        "users.json": {
            "users": [
                {
                    "name": "System Administrator",
                    "email": "admin@campus.edu",
                    "password": hash_pw("admin123"),
                    "role": "Admin",
                    "profile_picture": None
                },
                {
                    "name": "Dr. Alan Turing",
                    "email": "turing@campus.edu",
                    "password": hash_pw("faculty123"),
                    "role": "Faculty",
                    "profile_picture": None
                },
                {
                    "name": "Alice Smith",
                    "email": "alice@campus.edu",
                    "password": hash_pw("student123"),
                    "role": "Student",
                    "profile_picture": None
                }
            ]
        },
        "students.json": {
            "students": [
                {
                    "id": "S1001",
                    "name": "Alice Smith",
                    "email": "alice@campus.edu",
                    "department": "Computer Science",
                    "year": "3rd Year",
                    "phone": "+1 555-0101",
                    "enrollment_date": "2024-09-01"
                },
                {
                    "id": "S1002",
                    "name": "Bob Jones",
                    "email": "bob@campus.edu",
                    "department": "Electrical Engineering",
                    "year": "2nd Year",
                    "phone": "+1 555-0102",
                    "enrollment_date": "2025-09-01"
                },
                {
                    "id": "S1003",
                    "name": "Charlie Brown",
                    "email": "charlie@campus.edu",
                    "department": "Mechanical Engineering",
                    "year": "1st Year",
                    "phone": "+1 555-0103",
                    "enrollment_date": "2026-01-15"
                },
                {
                    "id": "S1004",
                    "name": "Diana Prince",
                    "email": "diana@campus.edu",
                    "department": "Computer Science",
                    "year": "4th Year",
                    "phone": "+1 555-0104",
                    "enrollment_date": "2023-09-01"
                },
                {
                    "id": "S1005",
                    "name": "Evan Wright",
                    "email": "evan@campus.edu",
                    "department": "Business Administration",
                    "year": "3rd Year",
                    "phone": "+1 555-0105",
                    "enrollment_date": "2024-09-01"
                }
            ]
        },
        "faculty.json": {
            "faculty": [
                {
                    "id": "F1001",
                    "name": "Dr. Alan Turing",
                    "email": "turing@campus.edu",
                    "department": "Computer Science",
                    "designation": "Professor",
                    "phone": "+1 555-0201",
                    "joining_date": "2018-08-15"
                },
                {
                    "id": "F1002",
                    "name": "Dr. Nikola Tesla",
                    "email": "tesla@campus.edu",
                    "department": "Electrical Engineering",
                    "designation": "Associate Professor",
                    "phone": "+1 555-0202",
                    "joining_date": "2020-01-10"
                },
                {
                    "id": "F1003",
                    "name": "Dr. Marie Curie",
                    "email": "curie@campus.edu",
                    "department": "Chemistry",
                    "designation": "Professor",
                    "phone": "+1 555-0203",
                    "joining_date": "2015-09-01"
                },
                {
                    "id": "F1004",
                    "name": "Prof. Ada Lovelace",
                    "email": "lovelace@campus.edu",
                    "department": "Computer Science",
                    "designation": "Assistant Professor",
                    "phone": "+1 555-0204",
                    "joining_date": "2022-03-01"
                }
            ]
        },
        "attendance.json": {
            "attendance": [
                {"id": "ATT001", "student_id": "S1001", "student_name": "Alice Smith", "date": "2026-07-10", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT002", "student_id": "S1002", "student_name": "Bob Jones", "date": "2026-07-10", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT003", "student_id": "S1003", "student_name": "Charlie Brown", "date": "2026-07-10", "status": "Absent", "marked_by": "turing@campus.edu"},
                {"id": "ATT004", "student_id": "S1004", "student_name": "Diana Prince", "date": "2026-07-10", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT005", "student_id": "S1005", "student_name": "Evan Wright", "date": "2026-07-10", "status": "Present", "marked_by": "turing@campus.edu"},
                
                {"id": "ATT006", "student_id": "S1001", "student_name": "Alice Smith", "date": "2026-07-13", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT007", "student_id": "S1002", "student_name": "Bob Jones", "date": "2026-07-13", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT008", "student_id": "S1003", "student_name": "Charlie Brown", "date": "2026-07-13", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT009", "student_id": "S1004", "student_name": "Diana Prince", "date": "2026-07-13", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT010", "student_id": "S1005", "student_name": "Evan Wright", "date": "2026-07-13", "status": "Absent", "marked_by": "turing@campus.edu"},
                
                {"id": "ATT011", "student_id": "S1001", "student_name": "Alice Smith", "date": "2026-07-14", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT012", "student_id": "S1002", "student_name": "Bob Jones", "date": "2026-07-14", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT013", "student_id": "S1003", "student_name": "Charlie Brown", "date": "2026-07-14", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT014", "student_id": "S1004", "student_name": "Diana Prince", "date": "2026-07-14", "status": "Present", "marked_by": "turing@campus.edu"},
                {"id": "ATT015", "student_id": "S1005", "student_name": "Evan Wright", "date": "2026-07-14", "status": "Present", "marked_by": "turing@campus.edu"}
            ]
        },
        "library.json": {
            "books": [
                {
                    "id": "B1001",
                    "title": "Introduction to Algorithms",
                    "author": "Thomas H. Cormen",
                    "isbn": "9780262033848",
                    "quantity": 5,
                    "available": 4,
                    "issued_to": [
                        {"student_id": "S1001", "student_name": "Alice Smith", "issue_date": "2026-07-08", "due_date": "2026-07-22"}
                    ]
                },
                {
                    "id": "B1002",
                    "title": "Clean Code",
                    "author": "Robert C. Martin",
                    "isbn": "9780132350884",
                    "quantity": 3,
                    "available": 3,
                    "issued_to": []
                },
                {
                    "id": "B1003",
                    "title": "Design Patterns",
                    "author": "Erich Gamma",
                    "isbn": "9780201633610",
                    "quantity": 4,
                    "available": 2,
                    "issued_to": [
                        {"student_id": "S1002", "student_name": "Bob Jones", "issue_date": "2026-07-05", "due_date": "2026-07-19"},
                        {"student_id": "S1004", "student_name": "Diana Prince", "issue_date": "2026-07-12", "due_date": "2026-07-26"}
                    ]
                }
            ]
        },
        "events.json": {
            "events": [
                {
                    "id": "EV001",
                    "title": "Annual Tech Symposium",
                    "description": "CS Department's largest technical event hosting coding combats and tech paper presentations.",
                    "date": "2026-09-15",
                    "time": "09:00",
                    "location": "Main Auditorium",
                    "category": "Academic"
                },
                {
                    "id": "EV002",
                    "title": "Intra-Campus Soccer Finals",
                    "description": "Final clash between Engineering and Business departments.",
                    "date": "2026-10-05",
                    "time": "16:00",
                    "location": "Campus Ground",
                    "category": "Sports"
                },
                {
                    "id": "EV003",
                    "title": "AI & Large Language Models Seminar",
                    "description": "Guest lecture by industry pioneer on agents and generative search systems.",
                    "date": "2026-08-20",
                    "time": "14:00",
                    "location": "Seminar Hall 2",
                    "category": "Workshop"
                }
            ]
        }
    }
    
    with db_lock:
        for filename, schema in default_schemas.items():
            path = get_file_path(filename)
            # Create file if missing or empty
            if not os.path.exists(path) or os.path.getsize(path) == 0:
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(schema, f, indent=2)
                except Exception as e:
                    print(f"Error initializing {filename}: {e}")

def read_db(filename):
    """Safely reads data from a JSON database file."""
    path = get_file_path(filename)
    with db_lock:
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error reading database {filename}: {e}")
            return {}

def write_db(filename, data):
    """Safely writes data to a JSON database file."""
    path = get_file_path(filename)
    with db_lock:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing to database {filename}: {e}")
            return False

# ==========================================
# USER CRUD HELPERS
# ==========================================
def get_all_users():
    data = read_db("users.json")
    return data.get("users", [])

def get_user_by_email(email):
    users = get_all_users()
    for user in users:
        if user.get("email").lower() == email.strip().lower():
            return user
    return None

def add_user(user_dict):
    data = read_db("users.json")
    users = data.get("users", [])
    
    # Check if duplicate email
    for u in users:
        if u.get("email").lower() == user_dict.get("email").lower():
            return False
            
    users.append(user_dict)
    data["users"] = users
    return write_db("users.json", data)

def update_user(email, updated_fields):
    data = read_db("users.json")
    users = data.get("users", [])
    updated = False
    
    for i, user in enumerate(users):
        if user.get("email").lower() == email.lower():
            users[i].update(updated_fields)
            updated = True
            break
            
    if updated:
        data["users"] = users
        return write_db("users.json", data)
    return False

# ==========================================
# STUDENT CRUD HELPERS
# ==========================================
def get_all_students():
    data = read_db("students.json")
    return data.get("students", [])

def add_student(student_dict):
    data = read_db("students.json")
    students = data.get("students", [])
    students.append(student_dict)
    data["students"] = students
    return write_db("students.json", data)

def update_student(student_id, updated_fields):
    data = read_db("students.json")
    students = data.get("students", [])
    updated = False
    
    for i, student in enumerate(students):
        if student.get("id") == student_id:
            students[i].update(updated_fields)
            updated = True
            break
            
    if updated:
        data["students"] = students
        return write_db("students.json", data)
    return False

def delete_student(student_id):
    data = read_db("students.json")
    students = data.get("students", [])
    original_len = len(students)
    students = [s for s in students if s.get("id") != student_id]
    
    if len(students) < original_len:
        data["students"] = students
        return write_db("students.json", data)
    return False

# ==========================================
# FACULTY CRUD HELPERS
# ==========================================
def get_all_faculty():
    data = read_db("faculty.json")
    return data.get("faculty", [])

def add_faculty(faculty_dict):
    data = read_db("faculty.json")
    faculties = data.get("faculty", [])
    faculties.append(faculty_dict)
    data["faculty"] = faculties
    return write_db("faculty.json", data)

def update_faculty(faculty_id, updated_fields):
    data = read_db("faculty.json")
    faculties = data.get("faculty", [])
    updated = False
    
    for i, fac in enumerate(faculties):
        if fac.get("id") == faculty_id:
            faculties[i].update(updated_fields)
            updated = True
            break
            
    if updated:
        data["faculty"] = faculties
        return write_db("faculty.json", data)
    return False

def delete_faculty(faculty_id):
    data = read_db("faculty.json")
    faculties = data.get("faculty", [])
    original_len = len(faculties)
    faculties = [f for f in faculties if f.get("id") != faculty_id]
    
    if len(faculties) < original_len:
        data["faculty"] = faculties
        return write_db("faculty.json", data)
    return False

# ==========================================
# ATTENDANCE CRUD HELPERS
# ==========================================
def get_all_attendance():
    data = read_db("attendance.json")
    return data.get("attendance", [])

def add_attendance_records(records_list):
    """Appends multiple attendance records at once."""
    data = read_db("attendance.json")
    attendance = data.get("attendance", [])
    attendance.extend(records_list)
    data["attendance"] = attendance
    return write_db("attendance.json", data)

def update_attendance_record(record_id, updated_fields):
    data = read_db("attendance.json")
    attendance = data.get("attendance", [])
    updated = False
    
    for i, record in enumerate(attendance):
        if record.get("id") == record_id:
            attendance[i].update(updated_fields)
            updated = True
            break
            
    if updated:
        data["attendance"] = attendance
        return write_db("attendance.json", data)
    return False

# ==========================================
# LIBRARY CRUD HELPERS
# ==========================================
def get_all_books():
    data = read_db("library.json")
    return data.get("books", [])

def add_book(book_dict):
    data = read_db("library.json")
    books = data.get("books", [])
    books.append(book_dict)
    data["books"] = books
    return write_db("library.json", data)

def update_book(book_id, updated_fields):
    data = read_db("library.json")
    books = data.get("books", [])
    updated = False
    
    for i, book in enumerate(books):
        if book.get("id") == book_id:
            books[i].update(updated_fields)
            updated = True
            break
            
    if updated:
        data["books"] = books
        return write_db("library.json", data)
    return False

def delete_book(book_id):
    data = read_db("library.json")
    books = data.get("books", [])
    original_len = len(books)
    books = [b for b in books if b.get("id") != book_id]
    
    if len(books) < original_len:
        data["books"] = books
        return write_db("library.json", data)
    return False

# ==========================================
# EVENTS CRUD HELPERS
# ==========================================
def get_all_events():
    data = read_db("events.json")
    return data.get("events", [])

def add_event(event_dict):
    data = read_db("events.json")
    events = data.get("events", [])
    events.append(event_dict)
    data["events"] = events
    return write_db("events.json", data)

def update_event(event_id, updated_fields):
    data = read_db("events.json")
    events = data.get("events", [])
    updated = False
    
    for i, event in enumerate(events):
        if event.get("id") == event_id:
            events[i].update(updated_fields)
            updated = True
            break
            
    if updated:
        data["events"] = events
        return write_db("events.json", data)
    return False

def delete_event(event_id):
    data = read_db("events.json")
    events = data.get("events", [])
    original_len = len(events)
    events = [e for e in events if e.get("id") != event_id]
    
    if len(events) < original_len:
        data["events"] = events
        return write_db("events.json", data)
    return False
