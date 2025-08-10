from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Avg, Count
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Job, JobTask
from .serializers import (
    JobSerializer, JobCreateSerializer, JobListSerializer,
    JobTaskSerializer, JobTaskCreateSerializer, TechnicianDashboardSerializer
)
from users.permissions import (
    IsAdminOrSalesAgent, IsAssignedTechnician, IsJobCreator, IsTechnicianUser
)


class JobListCreateView(generics.ListCreateAPIView):
    """
    List all jobs or create a new job (Admin/Sales Agent only)
    """
    queryset = Job.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'overdue', 'assigned_to']
    search_fields = ['title', 'client_name', 'description']
    ordering_fields = ['created_at', 'scheduled_date', 'priority']
    ordering = ['-created_at']
    permission_classes = [IsAdminOrSalesAgent]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return JobListSerializer
        return JobCreateSerializer


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a job
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAdminOrSalesAgent | IsAssignedTechnician | IsJobCreator]


class JobTaskListCreateView(generics.ListCreateAPIView):
    """
    List all tasks for a job or create a new task
    """
    serializer_class = JobTaskSerializer
    permission_classes = [IsAdminOrSalesAgent | IsAssignedTechnician]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return JobTask.objects.filter(job_id=job_id)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return JobTaskSerializer
        return JobTaskCreateSerializer
    
    def perform_create(self, serializer):
        job_id = self.kwargs.get('job_id')
        serializer.save(job_id=job_id)


class JobTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a job task
    """
    queryset = JobTask.objects.all()
    serializer_class = JobTaskSerializer
    permission_classes = [IsAdminOrSalesAgent | IsAssignedTechnician]


@extend_schema(
    responses={200: OpenApiResponse(description="Technician dashboard data")}
)
@api_view(['GET'])
@permission_classes([IsTechnicianUser])
def technician_dashboard_view(request):
    """
    Get all upcoming and in-progress tasks for the technician
    """
    user = request.user
    today = timezone.now().date()
    
    # Get tasks assigned to the technician
    tasks = JobTask.objects.filter(
        job__assigned_to=user,
        status__in=['pending', 'in_progress']
    ).select_related('job').prefetch_related('required_equipment')
    
    # Group by day
    dashboard_data = {}
    
    for task in tasks:
        job_date = task.job.scheduled_date.date()
        # Convert date to ISO format string for JSON serialization
        date_key = job_date.isoformat()
        if date_key not in dashboard_data:
            dashboard_data[date_key] = []
        
        serializer = TechnicianDashboardSerializer(task)
        dashboard_data[date_key].append(serializer.data)
    
    # Sort by date
    sorted_data = dict(sorted(dashboard_data.items()))
    
    return Response({
        'technician': user.username,
        'tasks_by_date': sorted_data
    })


@extend_schema(
    responses={
        200: OpenApiResponse(description="Admin analytics data"),
        403: OpenApiResponse(description="Admin access required")
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_analytics_view(request):
    """
    Admin analytics endpoint
    """
    # Check if user is admin
    if not request.user.is_admin:
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Calculate analytics
    total_jobs = Job.objects.count()
    completed_jobs = Job.objects.filter(status='completed').count()
    overdue_jobs = Job.objects.filter(overdue=True).count()
    
    # Average task completion time
    completed_tasks = JobTask.objects.filter(
        status='completed',
        completed_at__isnull=False
    )
    
    if completed_tasks.exists():
        # Use ExpressionWrapper for proper datetime arithmetic
        from django.db.models import ExpressionWrapper, F, DurationField
        avg_completion_time = completed_tasks.aggregate(
            avg_time=Avg(ExpressionWrapper(
                F('completed_at') - F('created_at'),
                output_field=DurationField()
            ))
        )['avg_time']
    else:
        avg_completion_time = None
    
    # Most used equipment
    equipment_usage = JobTask.objects.values(
        'required_equipment__name'
    ).annotate(
        usage_count=Count('required_equipment')
    ).order_by('-usage_count')[:10]
    
    # Jobs by status
    jobs_by_status = Job.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Jobs by priority
    jobs_by_priority = Job.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    return Response({
        'total_jobs': total_jobs,
        'completed_jobs': completed_jobs,
        'overdue_jobs': overdue_jobs,
        'completion_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        'avg_task_completion_time_hours': avg_completion_time.total_seconds() / 3600 if avg_completion_time else None,
        'most_used_equipment': equipment_usage,
        'jobs_by_status': jobs_by_status,
        'jobs_by_priority': jobs_by_priority,
    })


@extend_schema(
    request=OpenApiResponse(description="Task status update data"),
    responses={
        200: JobTaskSerializer,
        400: OpenApiResponse(description="Invalid status"),
        404: OpenApiResponse(description="Task not found")
    }
)
@api_view(['POST'])
@permission_classes([IsAssignedTechnician])
def update_task_status_view(request, task_id):
    """
    Update task status (Technician only)
    """
    try:
        task = JobTask.objects.get(id=task_id)
    except JobTask.DoesNotExist:
        return Response(
            {'error': 'Task not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    new_status = request.data.get('status')
    if new_status not in ['pending', 'in_progress', 'completed', 'cancelled']:
        return Response(
            {'error': 'Invalid status'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    task.status = new_status
    task.save()
    
    # Check if job can be completed
    if new_status == 'completed':
        job = task.job
        if job.can_be_completed:
            job.status = 'completed'
            job.save()
    
    serializer = JobTaskSerializer(task)
    return Response(serializer.data)
