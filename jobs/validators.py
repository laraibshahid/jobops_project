from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


def validate_scheduled_date_not_past(value):
    """
    Validate that scheduled date is not in the past
    """
    if value < timezone.now():
        raise ValidationError('Scheduled date cannot be in the past.')


def validate_job_can_be_completed(job):
    """
    Validate that all tasks are completed before marking job as completed
    """
    if not job.can_be_completed:
        raise ValidationError('Cannot complete job: not all tasks are completed.')


def validate_task_order_unique(job, order, task_id=None):
    """
    Validate that task order is unique within a job
    """
    existing_task = job.tasks.filter(order=order)
    if task_id:
        existing_task = existing_task.exclude(id=task_id)
    
    if existing_task.exists():
        raise ValidationError(f'Task with order {order} already exists in this job.')


def validate_equipment_availability(equipment_list, scheduled_date):
    """
    Validate that equipment is available for the scheduled date
    """
    # This is a placeholder for equipment availability logic
    # In a real system, you would check equipment scheduling conflicts
    pass


def validate_technician_availability(technician, scheduled_date):
    """
    Validate that technician is available for the scheduled date
    """
    # Check if technician has other jobs on the same date
    conflicting_jobs = technician.assigned_jobs.filter(
        scheduled_date__date=scheduled_date.date(),
        status__in=['pending', 'in_progress']
    )
    
    if conflicting_jobs.exists():
        raise ValidationError(f'Technician has conflicting jobs on {scheduled_date.date()}.') 