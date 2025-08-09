from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import User
from equipment.models import Equipment
from .validators import validate_scheduled_date_not_past, validate_job_can_be_completed


class Job(models.Model):
    """
    Main job model representing a complete job
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    client_name = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_jobs')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, validators=[MinValueValidator(1), MaxValueValidator(4)])
    scheduled_date = models.DateTimeField(validators=[validate_scheduled_date_not_past])
    overdue = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jobs'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.client_name}"
    
    def clean(self):
        """Custom validation"""
        if self.status == 'completed':
            validate_job_can_be_completed(self)
    
    def save(self, *args, **kwargs):
        # Check if job should be marked as overdue
        if self.scheduled_date and timezone.now() > self.scheduled_date:
            self.overdue = True
        
        # Validate before saving
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def can_be_completed(self):
        """Check if all tasks are completed before marking job as completed"""
        return all(task.status == 'completed' for task in self.tasks.all())


class JobTask(models.Model):
    """
    Individual tasks within a job
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    required_equipment = models.ManyToManyField(Equipment, blank=True, related_name='job_tasks')
    order = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'job_tasks'
        verbose_name = 'Job Task'
        verbose_name_plural = 'Job Tasks'
        ordering = ['job', 'order']
        unique_together = ['job', 'order']
    
    def __str__(self):
        return f"{self.job.title} - {self.title}"
    
    def clean(self):
        """Custom validation"""
        from .validators import validate_task_order_unique
        validate_task_order_unique(self.job, self.order, self.id)
    
    def save(self, *args, **kwargs):
        # Set completed_at when task is completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        
        # Validate before saving
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if task is overdue based on job scheduled date"""
        if self.job.scheduled_date and timezone.now() > self.job.scheduled_date:
            return True
        return False
