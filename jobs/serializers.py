from rest_framework import serializers
from .models import Job, JobTask
from users.serializers import UserListSerializer
from equipment.serializers import EquipmentListSerializer


class JobTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for JobTask model
    """
    required_equipment = EquipmentListSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = JobTask
        fields = [
            'id', 'job', 'title', 'description', 'status', 'required_equipment',
            'order', 'completed_at', 'created_at', 'updated_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue']


class JobTaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating JobTask (without read-only fields)
    """
    class Meta:
        model = JobTask
        fields = [
            'id', 'job', 'title', 'description', 'status', 'required_equipment',
            'order', 'completed_at'
        ]
        read_only_fields = ['id']


class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for Job model
    """
    created_by = UserListSerializer(read_only=True)
    assigned_to = UserListSerializer(read_only=True)
    tasks = JobTaskSerializer(many=True, read_only=True)
    can_be_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'client_name', 'created_by', 'assigned_to',
            'status', 'priority', 'scheduled_date', 'overdue', 'can_be_completed',
            'tasks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'can_be_completed']


class JobCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Job (without read-only fields)
    """
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'client_name', 'assigned_to',
            'status', 'priority', 'scheduled_date'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class JobListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing jobs (simplified)
    """
    created_by = UserListSerializer(read_only=True)
    assigned_to = UserListSerializer(read_only=True)
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'client_name', 'created_by', 'assigned_to',
            'status', 'priority', 'scheduled_date', 'overdue', 'task_count',
            'completed_task_count', 'created_at'
        ]
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_task_count(self, obj):
        return obj.tasks.filter(status='completed').count()


class TechnicianDashboardSerializer(serializers.ModelSerializer):
    """
    Serializer for technician dashboard
    """
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_client = serializers.CharField(source='job.client_name', read_only=True)
    required_equipment = EquipmentListSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = JobTask
        fields = [
            'id', 'job', 'job_title', 'job_client', 'title', 'description',
            'status', 'required_equipment', 'order', 'is_overdue', 'scheduled_date'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['scheduled_date'] = instance.job.scheduled_date
        return data 