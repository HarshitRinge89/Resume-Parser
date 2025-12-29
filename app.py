from flask import Flask, request, render_template ,url_for,redirect,session
from werkzeug.security import generate_password_hash, check_password_hash
import pdfplumber as pdp
import re 
import mysql.connector as sqltor

from dbm import sqlite3
conn= sqlite3.execute("resume_parser.db")
# mycon=sqltor.connect(host="localhost",user="root",passwd="utk@2801",database="resume_data")
if conn.is_connected()== False:
    print("Error connecting to mysql database.")
cursor=conn.cursor()

def read_pdf_resume(file):
    text = ""
    with pdp.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text

app = Flask(__name__) 
app.secret_key = "your_secret_key_here" 

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/recruiter_dashboard', methods=['GET', 'POST'])
def recruiter_dashboard():
    if request.method == 'POST':
        experience = int(request.form['experience'])
        required_skills = request.form['required_skills']
        skills_list = [skill.strip().lower() for skill in required_skills.split(",") if skill.strip()]

        query = "SELECT * FROM data WHERE exp_in_years >= ?"
        values = [experience]

        if skills_list:
            for skill in skills_list:
                query += " AND skills LIKE ?"
                values.append(f"%{skill}%")

        cursor.execute(query, tuple(values))
        results = cursor.fetchall()

        return render_template("recruiter_dashboard.html", candidates=results)

    return render_template("recruiter_dashboard.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result and check_password_hash(result[0], password) and role == result[1]:
            session['username'] = username
            if result[1] == "applicant":
                return redirect(url_for('applicant_dashboard')) 
            elif result[1] == "recruiter":
                return redirect(url_for('recruiter_dashboard'))
            else:
                return "Invalid user role!"
        else:
            return "Invalid username or password!"
    return render_template('login.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']

        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        role = request.form['role']

        if password != confirm_password:
            return "Passwords do not match!"
        
        hashed_password = generate_password_hash(password)

        sql = "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)"
        values = (username, email, hashed_password, role)
        cursor.execute(sql, values)
        conn.commit() 

        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/applicant_dashboard', methods=['GET', 'POST'])
def applicant_dashboard():
    if request.method == 'POST':
        file = request.files['file']
        resume_text = read_pdf_resume(file)
        resume_text = clean_text(resume_text)
        insert_data(resume_text)
        success_message = "Resume uploaded and data extracted successfully!"    
        return render_template("applicant_dashboard.html", message=success_message,name=session.get('username','default'))
    return render_template("applicant_dashboard.html")

skillset=["sql","java","spring boot","azure","git","excel","python","c#","javascript","c++"]
def extract_skills(resume_text):
    found=[]
    for skill in skillset:
        if skill in resume_text:
            found.append(skill)
    return list(set(found))

def extract_phone(resume_text):
    phone =re.findall(r'\b(?:\+91[\s-])[6-9]\d{9}\b',resume_text)
    phone=re.findall(r'\b[6-9]\d{9}\b', resume_text)
    return phone if phone else None

def extract_email(resume_text):
    email=re.search(r'[\w\.-]+@[\w\.-]+\.\w+',resume_text)
    return email.group() if email else None 

def insert_data(resume_text):
    name=session.get('username','default')
    phone=(extract_phone(resume_text))
    phone=phone[0] if phone else "0000000000"
    email=(extract_email(resume_text))
    experience= 3
    skills=",".join(extract_skills(resume_text))
    sql = "INSERT INTO data (name, phone, email, EXP_IN_YEARS, skills) VALUES (?, ?, ?, ?, ?)"
    values = (name, phone, email, experience, skills)
    cursor.execute(sql, values)
    conn.commit()
    
    if cursor.rowcount>0:
        print("Data inserted successfully.")
    else:
        print("Could not insert data.")
    
if __name__ == '__main__':
    app.run(debug=True)
