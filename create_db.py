import sqlite3

# Connect to SQLite DB
conn = sqlite3.connect("sample.db")
cursor = conn.cursor()

# --- Drop tables in dependency order ---
cursor.execute("DROP TABLE IF EXISTS employee_projects")
cursor.execute("DROP TABLE IF EXISTS projects")
cursor.execute("DROP TABLE IF EXISTS attendance")
cursor.execute("DROP TABLE IF EXISTS reviews")
cursor.execute("DROP TABLE IF EXISTS employees")
cursor.execute("DROP TABLE IF EXISTS departments")

# --- Departments table ---
cursor.execute("""
CREATE TABLE departments (
    dept_id INTEGER PRIMARY KEY,
    dept_name TEXT
)
""")

cursor.executemany("""
INSERT INTO departments (dept_id, dept_name) VALUES (?, ?)
""", [
    (1, 'HR'),
    (2, 'Engineering'),
    (3, 'Sales')
])

# --- Employees table ---
cursor.execute("""
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    dept_id INTEGER,
    salary INTEGER,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
)
""")

cursor.executemany("""
INSERT INTO employees (name, dept_id, salary) VALUES (?, ?, ?)
""", [
    ('Alice', 1, 60000),
    ('Bob', 2, 85000),
    ('Charlie', 3, 50000),
    ('David', 2, 90000),
])

# --- Reviews table ---
cursor.execute("""
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    review_date TEXT,
    rating INTEGER,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

cursor.executemany("""
INSERT INTO reviews (employee_id, review_date, rating) VALUES (?, ?, ?)
""", [
    (1, '2024-01-10', 4),
    (2, '2024-03-15', 5),
    (3, '2024-05-20', 3),
    (4, '2024-04-12', 4),
])

# --- Attendance table ---
cursor.execute("""
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    attendance_date TEXT,
    status TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

cursor.executemany("""
INSERT INTO attendance (employee_id, attendance_date, status) VALUES (?, ?, ?)
""", [
    (1, '2024-06-01', 'Present'),
    (2, '2024-06-01', 'Absent'),
    (3, '2024-06-01', 'Present'),
    (4, '2024-06-01', 'Absent'),
])

# --- Projects table ---
cursor.execute("""
CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY,
    project_name TEXT,
    dept_id INTEGER,
    start_date TEXT,
    end_date TEXT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
)
""")

cursor.executemany("""
INSERT INTO projects (project_name, dept_id, start_date, end_date) VALUES (?, ?, ?, ?)
""", [
    ('Payroll Automation', 1, '2024-01-01', '2024-03-30'),
    ('AI Chatbot', 2, '2024-02-15', '2024-06-30'),
    ('CRM Upgrade', 3, '2024-03-01', '2024-05-15'),
])

# --- Employee_Projects mapping table ---
cursor.execute("""
CREATE TABLE employee_projects (
    emp_id INTEGER,
    project_id INTEGER,
    PRIMARY KEY (emp_id, project_id),
    FOREIGN KEY (emp_id) REFERENCES employees(id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
)
""")

cursor.executemany("""
INSERT INTO employee_projects (emp_id, project_id) VALUES (?, ?)
""", [
    (1, 1),
    (2, 2),
    (4, 2),
    (3, 3),
])

# Commit and close
conn.commit()
conn.close()