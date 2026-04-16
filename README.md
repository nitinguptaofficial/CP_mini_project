# College Management System (Flask)

A beginner-friendly, modular college management web app with role-based dashboards for **Teacher** and **Student**.

## Features

- Authentication with role selection (Student / Teacher)
- Secure password hashing using Flask-Bcrypt
- CSRF-protected forms with Flask-WTF
- Attendance management with CSV export
- Assignment creation, submission, grading, and feedback
- Teacher and student analytics with Chart.js
- Secure file upload system (`pdf`, `doc`, `docx`, max 5MB)

## Project Structure

```
/project
 ├── app.py
 ├── config.py
 ├── models/
 ├── routes/
 ├── templates/
 ├── static/
 ├── forms/
 ├── utils/
 ├── uploads/
 └── requirements.txt
```

## Run Locally

```bash
cd /home/nitin/Documents/college/CP_MINI_PROJECT/project
python3 -m venv venv
source venv/bin/activate
export SECRET_KEY="your-local-secret-key"
pip install -r requirements.txt
python app.py
```

Open: `http://127.0.0.1:5000`

## Create Dummy Data

```bash
cd /home/nitin/Documents/college/CP_MINI_PROJECT/project
source ../venv/bin/activate
export SEED_PASSWORD="your-local-demo-password"
python seed_dummy_data.py
```

## Default Seed Accounts

The seed script creates demo users, but the password is read from `SEED_PASSWORD` so it is not stored in the repo.

## Environment Variables

Set these before running the app locally:

- `SECRET_KEY`: Flask session secret
- `SEED_PASSWORD`: Password used by the demo seed script

## Notes for Viva

- Code uses Flask blueprints for modular design.
- Models use SQLAlchemy relationships for easy joins.
- Role-based access is handled by a reusable decorator in `utils/decorators.py`.
- Analytics are generated server-side and rendered using Chart.js.
