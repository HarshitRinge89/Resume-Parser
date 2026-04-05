from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pdfplumber
import sqlite3
import re

app = Flask(__name__)

# DB connection
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# ================= INIT DB =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT,
    exp_in_years INTEGER,
    skills TEXT
)
""")

conn.commit()

# ================= HELPERS =================
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text.lower()

skillset = ["python","java","sql","javascript","c++","excel","git"]

def extract_skills(text):
    return [s for s in skillset if s in text]

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group() if match else ""

def extract_phone(text):
    match = re.search(r'[6-9]\d{9}', text)
    return match.group() if match else ""

# ================= AUTH =================
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    username = data["username"]
    email = data["email"]
    password = generate_password_hash(data["password"])
    role = data["role"]

    cursor.execute("INSERT INTO users (username,email,password,role) VALUES (?,?,?,?)",
                   (username,email,password,role))
    conn.commit()

    return jsonify({"message": "User created"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    username = data["username"]
    password = data["password"]

    cursor.execute("SELECT password, role FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user[0], password):
        return jsonify({"message": "Login success", "role": user[1]})
    
    return jsonify({"message": "Invalid credentials"}), 401

# ================= RESUME UPLOAD =================
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    text = read_pdf(file)
    
    skills = extract_skills(text)
    email = extract_email(text)
    phone = extract_phone(text)

    score = len(skills) * 10

    # store
    cursor.execute("INSERT INTO data (name, phone, email, exp_in_years, skills) VALUES (?,?,?,?,?)",
                   ("user", phone, email, 0, ",".join(skills)))
    conn.commit()

    return jsonify({
        "skills": skills,
        "email": email,
        "phone": phone,
        "experience": 0,
        "score": score
    })

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)