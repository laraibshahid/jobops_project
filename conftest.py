import pytest
import django
from django.conf import settings
from django.test import RequestFactory
from rest_framework.test import APIClient
from users.models import User
from jobs.models import Job, JobTask
from equipment.models import Equipment
from datetime import datetime, timedelta
from django.utils import timezone
import os

# Configure Django for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobops.settings')
django.setup()

@pytest.fixture
def api_client():
    """API client for testing"""
    return APIClient()

@pytest.fixture
def request_factory():
    """Request factory for testing"""
    return RequestFactory()

@pytest.fixture
def admin_user():
    """Create an admin user for testing"""
    user = User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='testpass123',
        is_admin=True,
        is_sales_agent=True
    )
    return user

@pytest.fixture
def sales_agent_user():
    """Create a sales agent user for testing"""
    user = User.objects.create_user(
        username='sales',
        email='sales@test.com',
        password='testpass123',
        is_admin=False,
        is_sales_agent=True
    )
    return user

@pytest.fixture
def technician_user():
    """Create a technician user for testing"""
    user = User.objects.create_user(
        username='technician',
        email='tech@test.com',
        password='testpass123',
        is_admin=False,
        is_sales_agent=False,
        is_technician=True
    )
    return user

@pytest.fixture
def regular_user():
    """Create a regular user for testing"""
    user = User.objects.create_user(
        username='user',
        email='user@test.com',
        password='testpass123',
        is_admin=False,
        is_sales_agent=False,
        is_technician=False
    )
    return user

@pytest.fixture
def equipment():
    """Create test equipment"""
    equipment = Equipment.objects.create(
        name='Test Equipment',
        description='Test equipment description',
        serial_number='TEST123',
        status='available'
    )
    return equipment

@pytest.fixture
def future_date():
    """Get a future date for testing"""
    return timezone.now() + timedelta(days=7)

@pytest.fixture
def past_date():
    """Get a past date for testing"""
    return timezone.now() - timedelta(days=7)

@pytest.fixture
def sample_job(admin_user, technician_user, future_date):
    """Create a sample job for testing"""
    job = Job.objects.create(
        title='Test Job',
        description='Test job description',
        client_name='Test Client',
        created_by=admin_user,
        assigned_to=technician_user,
        status='pending',
        priority=2,
        scheduled_date=future_date
    )
    return job

@pytest.fixture
def sample_job_task(sample_job, equipment):
    """Create a sample job task for testing"""
    task = JobTask.objects.create(
        job=sample_job,
        title='Test Task',
        description='Test task description',
        status='pending',
        order=1
    )
    task.required_equipment.add(equipment)
    return task

@pytest.fixture
def completed_job_task(sample_job, equipment):
    """Create a completed job task for testing"""
    task = JobTask.objects.create(
        job=sample_job,
        title='Completed Task',
        description='Completed task description',
        status='completed',
        order=2,
        completed_at=timezone.now()
    )
    task.required_equipment.add(equipment)
    return task 