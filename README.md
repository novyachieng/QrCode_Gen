# 🎓 University QR Authentication System

A secure QR code-based authentication system for university access control. This system allows students to generate time-limited QR codes for accessing various campus facilities and enables security personnel to verify them in real-time.

## ✨ Features

### Current Features
- ✅ **Secure Login System** - Student authentication with hashed passwords
- ✅ **QR Code Generation** - Time-limited (2 minutes) QR codes for access
- ✅ **Real-time Verification** - Security officers can verify QR codes instantly
- ✅ **Access Logging** - Complete audit trail of all access attempts
- ✅ **Multiple Access Areas** - Support for different campus locations
- ✅ **Countdown Timer** - Visual countdown for QR code expiry
- ✅ **Database Storage** - SQLite database for user management and logs
- ✅ **Responsive Design** - Works on desktop and mobile devices

### Technical Improvements Over Original
1. **Backend Connectivity** - Full API integration with Flask backend
2. **Database Implementation** - SQLite for persistent data storage
3. **Security Enhancements** - Password hashing, security tokens, CORS support
4. **Error Handling** - Comprehensive error handling and user feedback
5. **Access Logs** - Track and view all authentication activities
6. **Better UX** - Loading states, animations, and modern UI design
7. **Code Quality** - Modular, well-commented, production-ready code

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Navigate to project directory:**
   ```bash
   cd university-qr-system
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Step 1: Start the Backend Server
```bash
python app.py
```

You should see:
```
🚀 Starting University QR Authentication System
📊 Database initialized
🌐 Server running on http://localhost:5000
```

#### Step 2: Open the Frontend
Simply open `index.html` in your web browser:
- **Option A**: Double-click `index.html`
- **Option B**: Right-click → Open with → Your Browser
- **Option C**: Use a local server (recommended):
  ```bash
  # Using Python
  python -m http.server 8000
  # Then visit http://localhost:8000
  ```

## 🔐 Default Login Credentials

**Registration Number:** ICT/600/S23/118  
**Password:** Qr@Un1v#2026

## 📁 Project Structure

```
university-qr-system/
├── app.py                 # Flask backend server
├── index.html            # Main frontend interface
├── script.js             # JavaScript logic and API calls
├── style.css             # Styling and animations
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── university_qr.db     # SQLite database (auto-created)
```

## 🎯 How to Use

### For Students:

1. **Login** with your registration number and password
2. **Select Area** where you want to access (Library, Lab, etc.)
3. **Generate QR** - Click to create a 2-minute valid QR code
4. **Show to Security** - Display the QR code at the checkpoint
5. **View Logs** - Check your access history

### For Security Officers:

1. **Scan/Copy QR Data** from the student's screen
2. **Navigate to Verification** screen
3. **Paste QR Data** in the text area
4. **Verify** - System will grant or deny access
5. Access decision is shown with user details

## 🔧 Technical Details

### Backend API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/login` | POST | Authenticate user |
| `/generate-qr` | POST | Create QR code data |
| `/verify-qr` | POST | Verify QR code validity |
| `/access-logs` | GET | Retrieve access history |

### Database Schema

**users** table:
- id (PRIMARY KEY)
- regno (UNIQUE)
- password_hash
- full_name
- department
- year
- created_at

**access_logs** table:
- id (PRIMARY KEY)
- regno
- area
- action
- timestamp
- status

### Security Features

- ✅ Password hashing (SHA-256)
- ✅ Security tokens in QR codes
- ✅ Time-based expiry (2 minutes)
- ✅ CORS protection
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ Complete audit logging

## 🐛 Troubleshooting

### Backend Not Starting

**Issue:** `ModuleNotFoundError: No module named 'flask'`
```bash
pip install -r requirements.txt
```

**Issue:** `Address already in use`
```bash
# Kill the process using port 5000
# Linux/Mac:
lsof -ti:5000 | xargs kill -9
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Frontend Connection Issues

**Issue:** "Backend server not running" message

1. Ensure backend is running (`python app.py`)
2. Check browser console for errors (F12)
3. Verify `API_URL` in `script.js` matches backend address
4. Disable browser extensions that might block requests

### CORS Errors

If you see CORS errors in browser console:
- Ensure `flask-cors` is installed
- Restart the backend server
- Use a local server for frontend instead of file:// protocol

## 📝 Adding New Users

You can add users directly to the database or modify `app.py` to add during initialization:

```python
# In app.py, modify init_db() function:
password_hash = hashlib.sha256('NewPassword123'.encode()).hexdigest()
cursor.execute('''
    INSERT INTO users (regno, password_hash, full_name, department, year)
    VALUES (?, ?, ?, ?, ?)
''', ('ICT/600/S23/119', password_hash, 'New Student', 'CS', 'Year 2'))
```

## 🔄 API Testing with cURL

```bash
# Test login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"regno":"ICT/600/S23/118","password":"Qr@Un1v#2026"}'

# Generate QR
curl -X POST http://localhost:5000/generate-qr \
  -H "Content-Type: application/json" \
  -d '{"regno":"ICT/600/S23/118","area":"Library"}'

# Get access logs
curl http://localhost:5000/access-logs?regno=ICT/600/S23/118
```

## 🚀 Deployment Considerations

For production deployment:

1. **Use a production WSGI server** (Gunicorn, uWSGI):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Use PostgreSQL/MySQL** instead of SQLite for better concurrency

3. **Enable HTTPS** for secure communication

4. **Set environment variables** for sensitive data:
   ```python
   import os
   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
   ```

5. **Add rate limiting** to prevent abuse

6. **Implement proper authentication** with JWT tokens

## 📊 Future Enhancements

Potential features to add:
- [ ] Mobile app for students
- [ ] Admin dashboard
- [ ] Email notifications
- [ ] Multi-factor authentication
- [ ] Integration with student information system
- [ ] Biometric verification
- [ ] Real-time analytics
- [ ] Export access reports

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Check backend server logs
4. Verify all dependencies are installed

## 📄 License

This project is for educational purposes. Modify as needed for your institution.

---

**Built with ❤️ for University Security**
