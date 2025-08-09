from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model with role-based authentication
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('technician', 'Technician'),
        ('sales_agent', 'Sales Agent'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='technician')
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_technician(self):
        return self.role == 'technician'
    
    @property
    def is_sales_agent(self):
        return self.role == 'sales_agent'


class Equipment(models.Model):
    """
    Global equipment catalog
    """
    EQUIPMENT_TYPE_CHOICES = [
        ('tool', 'Tool'),
        ('machine', 'Machine'),
        ('vehicle', 'Vehicle'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES, default='tool')
    serial_number = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'equipment'
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"


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
    scheduled_date = models.DateTimeField()
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
    
    def save(self, *args, **kwargs):
        # Check if job should be marked as overdue
        if self.scheduled_date and timezone.now() > self.scheduled_date:
            self.overdue = True
        super().save(*args, **kwargs)
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def can_be_completed(self):
        """Check if all tasks are completed before marking job as completed"""
        return all(task.status == 'completed' for task in self.tasks.all())
