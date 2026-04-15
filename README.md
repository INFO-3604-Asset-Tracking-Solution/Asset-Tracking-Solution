# iGovTT Asset Tracking System

A web-based asset tracking and audit management system built for iGovTT. The application helps organisations manage assets, assignments, audit workflows, discrepancy reporting, notifications, and asset authorisation in a more structured and centralised way.

## Live Application

- Live App: https://info3604-asset-tracking-solution.onrender.com
- Repository: https://github.com/INFO-3604-Asset-Tracking-Solution/Asset-Tracking-Solution

## Overview

The iGovTT Asset Tracking System was developed to improve the way organisations manage physical assets and conduct audits. Instead of relying on manual processes, the system provides a centralised platform for tracking asset records, managing assignments, carrying out room-based audits, identifying discrepancies, and generating reports.

The system supports multiple user roles, including Administrators, Managers, and Auditors, with each role having access to different functions based on their responsibilities.

## Key Features

### Asset Management
- Add, view, edit, and delete asset records
- Store details such as asset tag, brand, model, serial number, status, and cost
- Search and filter assets using predefined criteria
- Export selected asset data

### Assignment Management
- Assign assets to employees and rooms
- View, update, and complete assignments
- Track active and completed assignments
- Automatically update assignment status when a return date is recorded

### Audit Management
- Start and manage audits for selected locations
- View expected assets for a room during an audit
- Record scan and check events in real time
- Maintain audit history and detailed audit reports
- Support manual entry and code-based scanning workflows

### Discrepancy Reporting
- Detect missing and relocated assets during audits
- View discrepancy reports with filtering and search support
- Reconcile discrepancies by updating status or location
- Export discrepancy reports

### Authorisation Workflow
- Allow auditors to propose new asset entries
- Allow administrators and managers to approve or reject proposed assets
- Maintain a history of authorisation actions

### Notifications
- Generate notifications related to discrepancies
- Support manager and admin review of important audit issues

### CSV Import and Export
- Bulk import asset and location records
- Download and export report data where needed

### Role-Based Access Control
- Separate permissions for Administrators, Managers, and Auditors
- Restrict access to actions based on role responsibilities

## Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask
- Flask-Cors
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Flask-Login
- Flask-Admin
- Flask-Mail
- Flask-Reuploaded

### Database
- PostgreSQL
- psycopg2-binary

### Deployment
- Render
- Gunicorn
- Gevent

### Testing and Performance
- pytest
- locust

### Utilities
- python-dotenv
- nanoid

## Project Structure

    flaskmvc-main/
    ├── App/
    │   ├── controllers/     # Business logic
    │   ├── models/          # Database models
    │   ├── views/           # Routes and blueprints
    │   ├── templates/       # Jinja2 HTML templates
    │   ├── static/          # CSS, JavaScript, images
    │   └── tests/           # Unit and integration tests
    ├── e2e/                 # End-to-end testing files
    ├── images/              # Project images/assets
    ├── requirements.txt     # Python dependencies
    ├── package.json         # Frontend/testing dependencies
    ├── render.yaml          # Render deployment configuration
    ├── gunicorn_config.py   # Gunicorn server configuration
    └── wsgi.py              # Application entry point

## Installation and Local Setup

### 1. Clone the repository

    git clone https://github.com/INFO-3604-Asset-Tracking-Solution/Asset-Tracking-Solution.git
    cd Asset-Tracking-Solution/flaskmvc-main/flaskmvc-main

### 2. Create and activate a virtual environment

    python -m venv venv
    source venv/bin/activate

On Windows:

    venv\Scripts\activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Configure environment variables

Create a `.flaskenv` or `.env` file in the project root and add the required variables.

Example:

    FLASK_APP=wsgi.py
    FLASK_DEBUG=True
    SECRET_KEY=your_secret_key
    JWT_SECRET_KEY=your_jwt_secret
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME=your_email
    MAIL_PASSWORD=your_app_password
    MAIL_DEFAULT_SENDER=noreply@example.com
    ENV=development

If using PostgreSQL locally, also configure your database connection variables.

## Running the Application

### Development

    flask run

### Production

    gunicorn -c gunicorn_config.py wsgi:app

## Database Setup

To initialise the database:

    flask init

If migrations are being used:

    flask db migrate -m "Initial migration"
    flask db upgrade

## Testing

### Run all tests

    pytest

or

    flask test

### Run performance tests

    locust

## Deployment

The application is deployed using **Render**.

### Production deployment includes
- Flask application hosted on Render
- PostgreSQL database connection
- Gunicorn as the production WSGI server
- Environment variables configured through the Render dashboard or deployment config

After deployment, database setup and migrations may need to be run from the Render shell:

    flask init
    flask db upgrade

## User Roles

### Administrator
- Manage user accounts and permissions
- Manage locations and asset data
- View audit history
- Review discrepancies and notifications

### Manager
- Approve or reject asset proposals
- Monitor audits and reports
- Review discrepancies
- Export reports

### Auditor
- Conduct room-based audits
- Scan and verify assets
- View audit history
- Propose new asset entries
- View discrepancy reports

## Screenshots

Screenshots of the system interface, including login pages, inventory, audit pages, and discrepancy reports, are available in the project documentation and report.

## Team

- Haley Skeete
- Kaitlyn Khan
- Kayla-Marie Maingot
- Jehlani Joseph

## Acknowledgements

This project was developed for INFO 3604 and designed around the needs of iGovTT’s asset tracking and audit workflow.

## License

This project was developed for academic purposes.
