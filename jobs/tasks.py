from celery import shared_task
from django.utils import timezone
from .models import Job


@shared_task
def check_overdue_jobs():
    """
    Check and update overdue jobs
    """
    now = timezone.now()
    overdue_jobs = Job.objects.filter(
        scheduled_date__lt=now,
        status__in=['pending', 'in_progress'],
        overdue=False
    )
    
    updated_count = 0
    for job in overdue_jobs:
        job.overdue = True
        job.save()
        updated_count += 1
    
    return f"Updated {updated_count} overdue jobs"


@shared_task
def cleanup_old_completed_jobs():
    """
    Clean up old completed jobs (optional maintenance task)
    """
    # Keep completed jobs for 1 year
    cutoff_date = timezone.now() - timezone.timedelta(days=365)
    old_jobs = Job.objects.filter(
        status='completed',
        updated_at__lt=cutoff_date
    )
    
    deleted_count = old_jobs.count()
    old_jobs.delete()
    
    return f"Deleted {deleted_count} old completed jobs"


@shared_task
def send_job_reminders():
    """
    Send reminders for upcoming jobs (placeholder for future implementation)
    """
    # This is a placeholder for sending email/SMS reminders
    # In a real system, you would integrate with email/SMS services
    upcoming_jobs = Job.objects.filter(
        scheduled_date__gte=timezone.now(),
        scheduled_date__lte=timezone.now() + timezone.timedelta(hours=24),
        status='pending'
    )
    
    reminder_count = 0
    for job in upcoming_jobs:
        # Send reminder logic would go here
        reminder_count += 1
    
    return f"Sent {reminder_count} job reminders" 