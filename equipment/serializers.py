from rest_framework import serializers
from .models import Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Equipment model
    """
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'type', 'serial_number', 'is_active', 
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EquipmentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing equipment (simplified)
    """
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'type', 'serial_number', 'is_active'] 