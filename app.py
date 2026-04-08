from flask import Flask, render_template, request, redirect, session, send_file
import os
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Kết nối MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="test"
)
cursor = conn.cursor()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["user"]
        p = request.form["pass"]

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
        user = cursor.fetchone()

        if user:
            session["user"] = u
            return redirect("/home")
    
    return render_template("login.html")

# ---------------- HOME ----------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    cursor.execute("SELECT * FROM files")
    files = cursor.fetchall()

    return render_template("home.html", files=files)

# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    cursor.execute(
        "INSERT INTO files (filename, path) VALUES (%s, %s)",
        (file.filename, path)
    )
    conn.commit()

    return redirect("/home")

# ---------------- DOWNLOAD ----------------
@app.route("/download/<int:id>")
def download(id):
    cursor.execute("SELECT path FROM files WHERE id=%s", (id,))
    result = cursor.fetchone()

    return send_file(result[0], as_attachment=True)

app.run(host="0.0.0.0", port=5000)
