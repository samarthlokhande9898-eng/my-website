from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, re
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")
DB_PATH = os.path.join(os.path.dirname(__file__), "cep_awareness.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, topic TEXT NOT NULL,
            message TEXT NOT NULL, created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, score INTEGER NOT NULL, total INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id))""")

@app.context_processor
def inject_user():
    return {"current_user": session.get("user")}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    questions = [
        {"q":"Which is a healthy way to respond to stress?", "opts":["Talk to someone you trust","Hide every problem","Try an addictive substance"], "a":0},
        {"q":"If a friend may be struggling with substance use, what is a helpful first step?", "opts":["Mock them","Listen without judging and encourage trusted help","Share their private story online"], "a":1},
        {"q":"Can habits and substance-use problems affect mental and physical health?", "opts":["No, never","Yes, they can","Only in adults"], "a":1},
        {"q":"What should you do if you feel unsafe or in immediate danger?", "opts":["Keep it secret","Contact a trusted adult or local emergency service","Wait and do nothing"], "a":1},
        {"q":"Which statement is most accurate?", "opts":["Asking for help is a sign of weakness","Support and professional care can help","People should handle every problem alone"], "a":1},
    ]
    if request.method == "POST":
        score = 0
        for i, q in enumerate(questions):
            try:
                if int(request.form.get(f"q{i}", -1)) == q["a"]:
                    score += 1
            except (TypeError, ValueError):
                pass
        user_id = session.get("user", {}).get("id")
        with db() as con:
            con.execute("INSERT INTO quiz_results(user_id, score, total, created_at) VALUES(?,?,?,?)",
                        (user_id, score, len(questions), datetime.utcnow().isoformat()))
        return render_template("quiz_result.html", score=score, total=len(questions))
    return render_template("quiz.html", questions=questions)

@app.route("/support", methods=["GET", "POST"])
def support():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:100]
        email = request.form.get("email", "").strip()[:160]
        topic = request.form.get("topic", "General question").strip()[:100]
        message = request.form.get("message", "").strip()[:2000]
        if not message:
            flash("Please write a message before submitting.", "error")
            return redirect(url_for("support"))
        with db() as con:
            con.execute("INSERT INTO messages(name,email,topic,message,created_at) VALUES(?,?,?,?,?)",
                        (name, email, topic, message, datetime.utcnow().isoformat()))
        flash("Your message was saved for this project demo. This form is not an emergency or confidential counselling service.", "success")
        return redirect(url_for("support"))
    return render_template("support.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:100]
        email = request.form.get("email", "").strip().lower()[:160]
        password = request.form.get("password", "")
        if not name or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            flash("Enter your name and a valid email address.", "error")
        elif len(password) < 8:
            flash("Use a password with at least 8 characters.", "error")
        else:
            try:
                with db() as con:
                    cur = con.execute("INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
                                      (name, email, generate_password_hash(password), datetime.utcnow().isoformat()))
                    user_id = cur.lastrowid
                session["user"] = {"id": user_id, "name": name, "email": email}
                flash("Account created successfully.", "success")
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                flash("An account with that email already exists. Please log in.", "error")
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user"] = {"id": user["id"], "name": user["name"], "email": user["email"]}
            return redirect(url_for("dashboard"))
        flash("Email or password was not recognised.", "error")
    return render_template("auth.html", mode="login")

@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        flash("Please log in to view your dashboard.", "error")
        return redirect(url_for("login"))
    with db() as con:
        results = con.execute("SELECT score,total,created_at FROM quiz_results WHERE user_id=? ORDER BY id DESC LIMIT 5",
                              (session["user"]["id"],)).fetchall()
    return render_template("dashboard.html", results=results)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "MindAware CEP", "database": "SQLite"})

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

init_db()
if __name__ == "__main__":
    app.run(debug=True)
