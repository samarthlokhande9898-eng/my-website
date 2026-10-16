# MindAware — Addiction Awareness CEP Website

A responsive college project website focused on addiction awareness, prevention, healthy coping, and encouraging people to seek trusted support.

## Features
- Home page with clear awareness messaging and calls to action
- Learning page covering warning signs, prevention, myths, and supportive responses
- Interactive awareness quiz; scores are stored in SQLite
- Register/login with password hashing and session-based dashboard
- Support/contact form that saves demo messages to SQLite
- Responsive navigation, accessible contrast, mobile layout
- `/health` endpoint for a quick backend check

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:
   `pip install -r requirements.txt`
5. Start the app:
   `python app.py`
6. Open `http://127.0.0.1:5000`

The database file `cep_awareness.db` is created automatically.

## Important project/demo notes
- This is an educational demo, not a medical service or crisis-response system.
- The support form stores messages locally; it does not send them to a counsellor.
- Do not enter real sensitive or private information into the demo.
- Before any public deployment, set a strong `SECRET_KEY`, turn off debug mode, add CSRF protection, rate limiting, secure cookie settings, privacy/retention controls, and a real support workflow.
- The content is educational and does not diagnose anyone. For immediate danger, contact a trusted adult and local emergency services.
