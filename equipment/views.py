from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Equipment
from .serializers import EquipmentSerializer, EquipmentListSerializer
from users.permissions import IsAdminUser


class EquipmentListCreateView(generics.ListCreateAPIView):
    """
    List all equipment or create new equipment (Admin only)
    """
    queryset = Equipment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_active']
    search_fields = ['name', 'serial_number', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EquipmentListSerializer
        return EquipmentSerializer


class EquipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete equipment (Admin only)
    """
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAdminUser]


class EquipmentListView(generics.ListAPIView):
    """
    List all active equipment (Read-only for all authenticated users)
    """
    queryset = Equipment.objects.filter(is_active=True)
    serializer_class = EquipmentListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type']
    search_fields = ['name', 'serial_number']
    ordering_fields = ['name', 'type']
    ordering = ['name']
