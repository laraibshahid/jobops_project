from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Jobs
    path('jobs/', views.JobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job-detail'),
    
    # Job Tasks
    path('jobs/<int:job_id>/tasks/', views.JobTaskListCreateView.as_view(), name='job-task-list-create'),
    path('tasks/<int:pk>/', views.JobTaskDetailView.as_view(), name='job-task-detail'),
    path('tasks/<int:task_id>/update-status/', views.update_task_status_view, name='update-task-status'),
    
    # Dashboard and Analytics
    path('technician-dashboard/', views.technician_dashboard_view, name='technician-dashboard'),
    path('admin-analytics/', views.admin_analytics_view, name='admin-analytics'),
] 