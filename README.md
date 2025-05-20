# School Management System

## Overview
A comprehensive school management system built with Django and React/TypeScript, featuring real-time analytics, secure role-based access, and an intuitive user interface.

## Features

### Authentication & Authorization
- Role-based access control (Admin/Student)
- Secure login with remember me functionality
- Password reset capabilities
- Session management

### Student Management
- Student profile management
- Enrollment tracking
- Academic performance monitoring
- Attendance tracking

### Course Management
- Course creation and management
- Assignment handling
- Grade management
- Course materials distribution

### Admin Dashboard
- Real-time analytics
- Student performance tracking
- Attendance monitoring
- Fee management
- Event scheduling

### User Interface
- Modern, responsive design
- Tailwind CSS for styling
- Real-time updates
- Intuitive navigation

## Tech Stack

### Backend
- Django 4.x
- Django REST Framework
- SQLite3 (can be configured for PostgreSQL)
- Python 3.x

### Frontend
- React 18.x
- TypeScript
- Tailwind CSS
- Vite

## Installation

### Prerequisites
- Python 3.x
- Node.js 16.x or higher
- npm or yarn

### Backend Setup
1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
```

2. Install Python dependencies:
```bash
cd school_management/backend
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

### Frontend Setup
1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Build the frontend assets:
```bash
npm run build
```

### Running the Application

1. Start the Django development server:
```bash
python manage.py runserver
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

The application will be available at:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## Development

### Backend Development
- Add new apps: `python manage.py startapp app_name`
- Make migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Run tests: `python manage.py test`

### Frontend Development
- Start development server: `npm run dev`
- Build for production: `npm run build`
- Run tests: `npm test`
- Lint code: `npm run lint`

## Project Structure
```
├── frontend/               # React/TypeScript frontend
│   ├── src/               # Source files
│   ├── public/            # Static files
│   └── package.json       # Frontend dependencies
├── school/                # Django project settings
├── school_management/     # Django apps
│   └── backend/          
│       └── school_app/    # Main Django app
├── static/                # Static files
├── staticfiles/           # Collected static files
└── manage.py             # Django management script
```

## Contributing
1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Django framework
- React framework
- Tailwind CSS
- All contributors to this project