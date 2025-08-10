# JobOps - Internal Operations Management System

A comprehensive Django-based system for managing job flows, multi-step tasks, and equipment tracking for internal teams (Sales, Technicians, Admins).

## Features

### Core Functionality
- **User Authentication & Role-Based Access**: JWT-based authentication with role-based permissions
- **Jobs Management**: Complete job lifecycle with multi-step tasks
- **Equipment Management**: Global equipment catalog with task linking
- **Technician Dashboard**: Daily view of upcoming and in-progress tasks
- **Admin Analytics**: Job performance metrics and equipment usage statistics
- **Background Tasks**: Automated overdue job detection and maintenance

### User Roles
- **Admin**: Full system access, user management, analytics
- **Sales Agent**: Create and manage jobs, view reports
- **Technician**: Update job progress, view assigned tasks

## Architecture

The project follows a modular Django app architecture:

```
jobops/
├── users/          # User management and authentication
├── jobs/           # Job and task management
├── equipment/      # Equipment catalog
├── audit/          # Change tracking and audit logs
└── jobops/         # Project configuration
```

## Technology Stack

- **Backend**: Django 4.2.23, Django REST Framework
- **Authentication**: JWT (SimpleJWT)
- **Background Tasks**: Celery with Redis
- **Database**: SQLite (development), PostgreSQL (production ready)
- **API Documentation**: Swagger/OpenAPI (drf-spectacular)
- **API Documentation**: Built-in DRF browsable API

## Installation & Setup

### Prerequisites
- Python 3.8+
- Redis (for Celery)
- Virtual environment

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd JobOps
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Environment Variables

The application uses the following environment variables (configured in `.env` file):

```bash
# Django Configuration
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
DJANGO_LOGLEVEL=INFO
DJANGO_ALLOWED_HOSTS=localhost

# Database Configuration (PostgreSQL)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=internalops
DATABASE_USERNAME=admin
DATABASE_PASSWORD=admin@!@#
DATABASE_HOST=db
DATABASE_PORT=5432

# Optional: Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**Important Notes:**
- Replace `your_secret_key` with a secure secret key for production
- Set `DEBUG=False` in production
- Update `DJANGO_ALLOWED_HOSTS` with your domain in production
- Ensure PostgreSQL is running and accessible with the configured credentials

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   python manage.py loaddata fixtures/sample_data.json
   ```

8. **Start the development server**
   ```bash
   python manage.py runserver
   ```

### Running Background Tasks

1. **Start Redis server**
   ```bash
   redis-server
   ```

2. **Start Celery worker**
   ```bash
   celery -A jobops worker -l info
   ```

3. **Start Celery beat (for scheduled tasks)**
   ```bash
   celery -A jobops beat -l info
   ```

## API Endpoints

### API Documentation
- `GET /api/schema/` - OpenAPI schema (JSON/YAML)
- `GET /api/docs/` - Swagger UI documentation
- `GET /api/redoc/` - ReDoc documentation

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get current user info
- `POST /api/auth/change-password/` - Change password

### User Management (Admin only)
- `GET /api/auth/users/` - List all users
- `POST /api/auth/users/` - Create new user
- `GET /api/auth/users/{id}/` - Get user details
- `PUT /api/auth/users/{id}/` - Update user
- `DELETE /api/auth/users/{id}/` - Delete user

### Jobs
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create new job (Admin/Sales)
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job
- `DELETE /api/jobs/{id}/` - Delete job

### Job Tasks
- `GET /api/jobs/{job_id}/tasks/` - List tasks for a job
- `POST /api/jobs/{job_id}/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `POST /api/tasks/{id}/update-status/` - Update task status (Technician)

### Equipment
- `GET /api/equipment/` - List all equipment (Admin)
- `POST /api/equipment/` - Create equipment (Admin)
- `GET /api/equipment/{id}/` - Get equipment details
- `PUT /api/equipment/{id}/` - Update equipment
- `DELETE /api/equipment/{id}/` - Delete equipment
- `GET /api/equipment/list/` - List active equipment (Read-only)

### Dashboard & Analytics
- `GET /api/technician-dashboard/` - Technician dashboard
- `GET /api/admin-analytics/` - Admin analytics (Admin only)

## Business Rules

### Job Lifecycle
1. Jobs can only be completed when all tasks are completed
2. Tasks must be completed in order (based on order field)
3. Overdue jobs are automatically flagged
4. Only assigned technicians can update job/task progress

### Permissions
- **Admins**: Full access to all features
- **Sales Agents**: Can create/edit jobs, view reports
- **Technicians**: Can update assigned job progress, view dashboard

### Validation Rules
- Scheduled dates cannot be in the past
- Task order must be unique within a job
- Equipment must be available for scheduled tasks
- Technician availability is checked for scheduling conflicts

## Background Tasks

### Scheduled Tasks
- **Overdue Job Detection**: Runs every hour
- **Job Reminders**: Runs every 6 hours
- **Cleanup Old Jobs**: Runs weekly

### Manual Tasks
```python
from jobs.tasks import check_overdue_jobs, send_job_reminders

# Run manually
check_overdue_jobs.delay()
send_job_reminders.delay()
```

## Sample Data

The system includes sample data with:
- 3 users (admin, technician, sales agent)
- 3 equipment items (drill, helmet, van)
- 2 jobs with multiple tasks
- Various task statuses and equipment assignments

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project follows PEP 8 standards. Use a linter like `flake8` for code quality.

### Adding New Features
1. Create new app if needed: `python manage.py startapp app_name`
2. Add models, serializers, views, and URLs
3. Update permissions if needed
4. Add tests
5. Update documentation

## Production Deployment

### Environment Variables
```bash
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
DJANGO_LOGLEVEL=WARNING

# Database Configuration
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=your_database_name
DATABASE_USERNAME=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=your_database_host
DATABASE_PORT=5432

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Database
- Use PostgreSQL for production
- Set up proper database backups
- Configure connection pooling

### Security
- Use HTTPS in production
- Set secure JWT settings
- Configure CORS properly
- Use environment variables for secrets


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
## Support

For support and questions, please contact the development team or create an issue in the repository. 
# jobops_project



## Django App — DevOps & Deployment

### Overview
This repository contains:
- Dockerfile — (non-root)
- .github/workflows/ci.yml — CI: tests + build + push to GHCR
- docker-compose.yml — run jobops + Postgres on EC2

### How to deploy (manual)
1. Provision EC2 with IAM role that has AmazonSSMManagedInstanceCore.
2. SSH/SSM into EC2:
   ```bash
   cd /home/ubuntu/jobops
   # create .env securely
   docker-compose pull
   docker-compose up -d
   ```