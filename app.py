from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import secrets, sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
CORS(app)

DB_FILE = 'university_qr.db'

# -------------------------
# DATABASE INITIALIZATION
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regno TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            department TEXT,
            year TEXT,
            role TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    
    
    # Access logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regno TEXT NOT NULL,
            area TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL
        )
    ''')

    # Add default user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE regno = ?', ('ICT/600/S23/118',))
    if cursor.fetchone()[0] == 0:
        password_hash = generate_password_hash('Qr@Un1v#2026')
        cursor.execute('''
            INSERT INTO users (regno, password_hash, full_name, department, year, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('ICT/600/S23/118', password_hash, 'Test Student', 'ICT', 'Year 3', 'student'))
        # QR Tokens table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS qr_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        regno TEXT NOT NULL,
        area TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires TIMESTAMP NOT NULL,
        used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

    conn.commit()
    conn.close()
init_db()

# -------------------------
# HELPER FUNCTIONS
# -------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def log_access(regno, area, action, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO access_logs (regno, area, action, status)
        VALUES (?, ?, ?, ?)
    ''', (regno, area, action, status))
    conn.commit()
    conn.close()

# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

# -------------------------
# SIGNUP
# -------------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    regno = data.get("regno", "").strip()
    full_name = data.get("full_name", "").strip()
    department = data.get("department", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "student")
    year = data.get("year", "").strip()  # optional

    if not all([full_name, regno, department, password]):
        return jsonify({"message": "All fields are required"}), 400

    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (regno, full_name, department, password_hash, role, year)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (regno, full_name, department, password_hash, role, year))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"message": "Registration number already exists"}), 400

    conn.close()
    return jsonify({"message": "Account created successfully"}), 201

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    regno = data.get("regno", "").strip()
    password = data.get("password", "").strip()

    if not regno or not password:
        return jsonify({"status": "error", "message": "Registration number and password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT regno, full_name, department, year, role, password_hash
        FROM users
        WHERE regno = ?
    ''', (regno,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        log_access(regno, "Login", "System", "Success")
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": {
                "regno": user['regno'],
                "name": user['full_name'],
                "department": user['department'],
                "year": user['year'],
                "role": user['role']
            }
        })
    else:
        log_access(regno or "unknown", "Login", "System", "Failed")
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401


# -------------------------
# QR GENERATION
# -------------------------

@app.route("/generate-qr", methods=["POST"])
def generate_qr():
    try:
        data = request.get_json()
        regno = data.get("regno", "").strip()
        area = data.get("area", "").strip()

        if not regno or not area:
            return jsonify({"status": "error", "message": "Missing data"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT full_name FROM users WHERE regno = ?', (regno,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({"status": "error", "message": "User not found"}), 404

        expiry_time = datetime.utcnow() + timedelta(minutes=2)
        token = secrets.token_hex(16)

        # Save token to database
        cursor.execute('''
            INSERT INTO qr_tokens (regno, area, token, expires)
            VALUES (?, ?, ?, ?)
        ''', (regno, area, token, expiry_time.isoformat()))

        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "data": {
                "token": token,
                "expires": expiry_time.isoformat()
            }
        })

    except Exception as e:
        print("QR ERROR:", e)
        return jsonify({"status": "error", "message": "Server error"}), 500

# ACCESS LOGS
# -------------------------
@app.route("/access-logs")
def access_logs():
    regno = request.args.get("regno")
    limit = int(request.args.get("limit", 20))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM access_logs
        WHERE regno = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (regno, limit))
    logs = cursor.fetchall()
    conn.close()
    logs_list = [dict(log) for log in logs]
    return jsonify({"status": "success", "logs": logs_list})

# -------------------------
# VERIFY QR
# -------------------------

@app.route("/verify-qr", methods=["POST"])
def verify_qr():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"access": "DENIED", "reason": "Invalid QR"})

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT regno, area, expires, used
        FROM qr_tokens
        WHERE token = ?
    ''', (token,))

    record = cursor.fetchone()

    if not record:
        conn.close()
        return jsonify({"access": "DENIED", "reason": "Invalid token"})

    regno, area, expires, used = record

    if used == 1:
        conn.close()
        return jsonify({"access": "DENIED", "reason": "QR already used"})

    if datetime.fromisoformat(expires) < datetime.utcnow():
        conn.close()
        return jsonify({"access": "DENIED", "reason": "QR expired"})

    # Mark token as used
    cursor.execute('UPDATE qr_tokens SET used = 1 WHERE token = ?', (token,))
    conn.commit()

    # Get user info
    cursor.execute('SELECT full_name FROM users WHERE regno = ?', (regno,))
    user = cursor.fetchone()

    conn.close()

    return jsonify({
        "access": "GRANTED",
        "user": {"regno": regno, "name": user['full_name']},
        "area": area,
        "verified_at": datetime.utcnow().isoformat()
    })

# RUN SERVER
# -------------------------
if __name__ == "__main__":
    print("🚀 University QR Authentication System starting...")
    print("🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
