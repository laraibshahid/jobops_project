from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from users.models import User
from equipment.models import Equipment
from .models import Job, JobTask
from .validators import validate_scheduled_date_not_past, validate_job_can_be_completed


class JobModelTest(TestCase):
    """Test cases for Job model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_admin=True,
            is_sales_agent=True
        )
        
        self.technician_user = User.objects.create_user(
            username='technician',
            email='tech@test.com',
            password='testpass123',
            is_admin=False,
            is_sales_agent=False,
            is_technician=True
        )
        
        self.future_date = timezone.now() + timedelta(days=7)
        self.past_date = timezone.now() - timedelta(days=7)
    
    def test_job_creation(self):
        """Test job creation with valid data"""
        job = Job.objects.create(
            title='Test Job',
            description='Test job description',
            client_name='Test Client',
            created_by=self.admin_user,
            assigned_to=self.technician_user,
            status='pending',
            priority=2,
            scheduled_date=self.future_date
        )
        
        self.assertEqual(job.title, 'Test Job')
        self.assertEqual(job.client_name, 'Test Client')
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.priority, 2)
        self.assertEqual(job.created_by, self.admin_user)
        self.assertEqual(job.assigned_to, self.technician_user)
        self.assertFalse(job.overdue)
        self.assertIsNotNone(job.created_at)
        self.assertIsNotNone(job.updated_at)
    
    def test_job_string_representation(self):
        """Test job string representation"""
        job = Job.objects.create(
            title='Test Job',
            description='Test description',
            client_name='Test Client',
            created_by=self.admin_user,
            scheduled_date=self.future_date
        )
        
        expected = f"Test Job - Test Client"
        self.assertEqual(str(job), expected)
    
    def test_job_default_values(self):
        """Test job default values"""
        job = Job.objects.create(
            title='Test Job',
            description='Test description',
            client_name='Test Client',
            created_by=self.admin_user,
            scheduled_date=self.future_date
        )
        
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.priority, 2)
        self.assertFalse(job.overdue)
    
    def test_job_priority_validation(self):
        """Test job priority validation"""
        # Test valid priorities
        for priority in [1, 2, 3, 4]:
            job = Job.objects.create(
                title=f'Test Job {priority}',
                description='Test description',
                client_name='Test Client',
                created_by=self.admin_user,
                priority=priority,
                scheduled_date=self.future_date
            )
            self.assertEqual(job.priority, priority)
        
        # Test invalid priorities
        with self.assertRaises(ValidationError):
            job = Job(
                title='Invalid Priority Job',
                description='Test description',
                client_name='Test Client',
                created_by=self.admin_user,
                priority=0,  # Invalid
                scheduled_date=self.future_date
            )
            job.full_clean()
        
        with self.assertRaises(ValidationError):
            job = Job(
                title='Invalid Priority Job 2',
                description='Test description',
                client_name='Test Client',
                created_by=self.admin_user,
                priority=5,  # Invalid
                scheduled_date=self.future_date
            )
            job.full_clean()
    
    def test_job_status_choices(self):
        """Test job status choices"""
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        
        for status in valid_statuses:
            job = Job.objects.create(
                title=f'Test Job {status}',
                description='Test description',
                client_name='Test Client',
                created_by=self.admin_user,
                status=status,
                scheduled_date=self.future_date
            )
            self.assertEqual(job.status, status)
    
    def test_job_properties(self):
        """Test job properties"""
        job = Job.objects.create(
            title='Test Job',
            description='Test description',
            client_name='Test Client',
            created_by=self.admin_user,
            status='pending',
            scheduled_date=self.future_date
        )
        
        # Test is_completed property
        self.assertFalse(job.is_completed)
        job.status = 'completed'
        self.assertTrue(job.is_completed)
        
        # Test can_be_completed property (no tasks yet)
        self.assertTrue(job.can_be_completed)
    
    def test_job_overdue_logic(self):
        """Test automatic overdue flag setting"""
        # Create job with past date
        job = Job.objects.create(
            title='Overdue Job',
            description='Test description',
            client_name='Test Client',
            created_by=self.admin_user,
            scheduled_date=self.past_date
        )
        
        # Job should be marked as overdue
        self.assertTrue(job.overdue)
        
        # Create job with future date
        future_job = Job.objects.create(
            title='Future Job',
            description='Test description',
            client_name='Test Client',
            created_by=self.admin_user,
            scheduled_date=self.future_date
        )
        
        # Job should not be overdue
        self.assertFalse(future_job.overdue)
    
    def test_job_ordering(self):
        """Test job ordering by creation date"""
        # Create jobs in reverse order
        job2 = Job.objects.create(
            title='Second Job',
            description='Test description',
            client_name='Test Client',
            created_by=self.admin_user,
            scheduled_date=self.future_date
        )
        
        job1 = Job.objects.create(
            title='First Job',
            description='Test description',
            client_name='Test Client',
            created_by=self.admin_user,
            scheduled_date=self.future_date
        )
        
        # Jobs should be ordered by created_at descending
        jobs = Job.objects.all()
        self.assertEqual(jobs[0], job1)  # Most recent first
        self.assertEqual(jobs[1], job2)  # Older second


class JobTaskModelTest(TestCase):
    """Test cases for JobTask model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_admin=True
        )
        
        self.technician_user = User.objects.create_user(
            username='technician',
            email='tech@test.com',
            password='testpass123',
            is_technician=True
        )
        
        self.future_date = timezone.now() + timedelta(days=7)
        
        self.job = Job.objects.create(
            title='Test Job',
            description='Test job description',
            client_name='Test Client',
            created_by=self.admin_user,
            assigned_to=self.technician_user,
            scheduled_date=self.future_date
        )
        
        self.equipment = Equipment.objects.create(
            name='Test Equipment',
            description='Test equipment description',
            serial_number='TEST123',
            status='available'
        )
    
    def test_job_task_creation(self):
        """Test job task creation with valid data"""
        task = JobTask.objects.create(
            job=self.job,
            title='Test Task',
            description='Test task description',
            status='pending',
            order=1
        )
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.job, self.job)
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.order, 1)
        self.assertIsNone(task.completed_at)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
    
    def test_job_task_string_representation(self):
        """Test job task string representation"""
        task = JobTask.objects.create(
            job=self.job,
            title='Test Task',
            description='Test description',
            status='pending',
            order=1
        )
        
        expected = f"Test Job - Test Task"
        self.assertEqual(str(task), expected)
    
    def test_job_task_default_values(self):
        """Test job task default values"""
        task = JobTask.objects.create(
            job=self.job,
            title='Test Task',
            description='Test description',
            order=1
        )
        
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.order, 1)
        self.assertIsNone(task.completed_at)
    
    def test_job_task_status_choices(self):
        """Test job task status choices"""
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        
        for status in valid_statuses:
            task = JobTask.objects.create(
                job=self.job,
                title=f'Test Task {status}',
                description='Test description',
                status=status,
                order=valid_statuses.index(status) + 1
            )
            self.assertEqual(task.status, status)
    
    def test_job_task_completed_at_logic(self):
        """Test automatic completed_at timestamp setting"""
        task = JobTask.objects.create(
            job=self.job,
            title='Test Task',
            description='Test description',
            status='pending',
            order=1
        )
        
        # Initially no completed_at
        self.assertIsNone(task.completed_at)
        
        # Mark as completed
        task.status = 'completed'
        task.save()
        
        # Should have completed_at timestamp
        self.assertIsNotNone(task.completed_at)
        
        # Change back to pending
        task.status = 'pending'
        task.save()
        
        # completed_at should be cleared
        self.assertIsNone(task.completed_at)
    
    def test_job_task_equipment_relationship(self):
        """Test many-to-many relationship with equipment"""
        task = JobTask.objects.create(
            job=self.job,
            title='Test Task',
            description='Test description',
            status='pending',
            order=1
        )
        
        # Add equipment
        task.required_equipment.add(self.equipment)
        
        # Check relationship
        self.assertEqual(task.required_equipment.count(), 1)
        self.assertEqual(task.required_equipment.first(), self.equipment)
        
        # Check reverse relationship
        self.assertEqual(self.equipment.job_tasks.count(), 1)
        self.assertEqual(self.equipment.job_tasks.first(), task)
    
    def test_job_task_ordering(self):
        """Test job task ordering by job and order"""
        # Create tasks with different orders
        task2 = JobTask.objects.create(
            job=self.job,
            title='Second Task',
            description='Test description',
            order=2
        )
        
        task1 = JobTask.objects.create(
            job=self.job,
            title='First Task',
            description='Test description',
            order=1
        )
        
        # Tasks should be ordered by job and order
        tasks = JobTask.objects.all()
        self.assertEqual(tasks[0], task1)  # Order 1 first
        self.assertEqual(tasks[1], task2)  # Order 2 second
    
    def test_job_task_overdue_property(self):
        """Test overdue property calculation"""
        # Create task for job with future date
        future_task = JobTask.objects.create(
            job=self.job,
            title='Future Task',
            description='Test description',
            order=1
        )
        
        # Should not be overdue
        self.assertFalse(future_task.is_overdue)
        
        # Create job with past date
        past_job = Job.objects.create(
            title='Past Job',
            description='Test description',
            client_name='Test Client',
            created_by=self.admin_user,
            scheduled_date=timezone.now() - timedelta(days=7)
        )
        
        past_task = JobTask.objects.create(
            job=past_job,
            title='Past Task',
            description='Test description',
            order=1
        )
        
        # Should be overdue
        self.assertTrue(past_task.is_overdue)


class JobTaskOrderValidationTest(TestCase):
    """Test cases for job task order validation"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_admin=True
        )
        
        self.future_date = timezone.now() + timedelta(days=7)
        
        self.job = Job.objects.create(
            title='Test Job',
            description='Test job description',
            client_name='Test Client',
            created_by=self.admin_user,
            scheduled_date=self.future_date
        )
    
    def test_unique_order_per_job(self):
        """Test that order must be unique per job"""
        # Create first task
        task1 = JobTask.objects.create(
            job=self.job,
            title='First Task',
            description='Test description',
            order=1
        )
        
        # Create second task with same order (should fail)
        with self.assertRaises(Exception):  # Database constraint violation
            task2 = JobTask.objects.create(
                job=self.job,
                title='Second Task',
                description='Test description',
                order=1  # Same order as first task
            )
        
        # Create second task with different order (should succeed)
        task2 = JobTask.objects.create(
            job=self.job,
            title='Second Task',
            description='Test description',
            order=2
        )
        
        self.assertEqual(JobTask.objects.count(), 2)
    
    def test_order_can_be_reused_across_jobs(self):
        """Test that order can be reused across different jobs"""
        # Create second job
        job2 = Job.objects.create(
            title='Test Job 2',
            description='Test job description 2',
            client_name='Test Client 2',
            created_by=self.admin_user,
            scheduled_date=self.future_date
        )
        
        # Create tasks with same order in different jobs
        task1 = JobTask.objects.create(
            job=self.job,
            title='Task in Job 1',
            description='Test description',
            order=1
        )
        
        task2 = JobTask.objects.create(
            job=job2,
            title='Task in Job 2',
            description='Test description',
            order=1  # Same order, different job
        )
        
        # Both should be created successfully
        self.assertEqual(JobTask.objects.count(), 2)
        self.assertEqual(task1.order, 1)
        self.assertEqual(task2.order, 1)
