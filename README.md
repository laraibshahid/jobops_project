# JobOps - Internal Operations Management System

A comprehensive Django-based system for managing job flows, multi-step tasks, and equipment tracking for internal teams (Sales, Technicians, Admins).

**Repository**: [https://github.com/laraibshahid/jobops_project.git](https://github.com/laraibshahid/jobops_project.git)

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
   git clone https://github.com/laraibshahid/jobops_project.git
   cd jobops_project
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
   # Create .env file with your configuration
   # See Environment Variables section below
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
- **For development without PostgreSQL**: The project includes SQLite fallback in `db.sqlite3`

**⚠️ Current Issue**: The project is currently configured to use PostgreSQL but the database credentials in settings.py are not properly configured. For immediate development, the SQLite database (`db.sqlite3`) should work without additional configuration.

5. **Run migrations**
   ```bash
   python3 manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python3 manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   python3 manage.py loaddata fixtures/sample_data.json
   ```

8. **Start the development server**
   
   **Option 1: Using manage.sh (Recommended)**
   ```bash
   ./manage.sh runserver
   ```
   
   **Option 2: Direct Django command**
   ```bash
   python3 manage.py runserver
   ```

### Troubleshooting Common Issues

#### Database Connection Issues
If you encounter "ImproperlyConfigured: settings.DATABASES is improperly configured" error:

1. **For Development (SQLite)**: The project includes a pre-configured SQLite database (`db.sqlite3`) that should work out of the box.

2. **For PostgreSQL**: Ensure your `.env` file contains valid database credentials:
   ```bash
   DATABASE_NAME=your_db_name
   DATABASE_USERNAME=your_db_user
   DATABASE_PASSWORD=your_db_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   ```

3. **Check Database Status**:
   ```bash
   python3 manage.py check --database default
   ```

#### Sample Data Loading Issues
If fixture loading fails:
1. Ensure the database is properly configured
2. Check that migrations have been applied
3. Verify the fixture file exists: `fixtures/sample_data.json`

#### Port Already in Use
If port 8000 is already in use:
```bash
# Find processes using port 8000
lsof -ti:8000

# Kill processes on port 8000
kill -9 $(lsof -ti:8000)
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
- `POST /api/login/` - User login (Note: NOT `/api/auth/login/`)
- `POST /api/token/refresh/` - Refresh JWT token
- `GET /api/profile/` - Get current user info
- `POST /api/change-password/` - Change password

### User Management (Admin only)
- `GET /api/users/` - List all users
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

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
python3 manage.py test
```

### Code Style
The project follows PEP 8 standards. Use a linter like `flake8` for code quality.

### Adding New Features
1. Create new app if needed: `python3 manage.py startapp app_name`
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

## Docker Deployment

### Using Docker Compose
```bash
# Start the services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Deployment
1. Provision EC2 with IAM role that has AmazonSSMManagedInstanceCore
2. SSH/SSM into EC2:
   ```bash
   cd /home/ubuntu/jobops
   # create .env securely
   docker-compose pull
   docker-compose up -d
   ```

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

## Repository Information

- **GitHub**: [https://github.com/laraibshahid/jobops_project.git](https://github.com/laraibshahid/jobops_project.git)
- **Main Branch**: `main`
- **Language**: Python (97.5%), Dockerfile (1.8%), Shell (0.7%)
- **CI/CD**: GitHub Actions with automated testing and Docker image building
- **Container Registry**: GitHub Container Registry (GHCR)