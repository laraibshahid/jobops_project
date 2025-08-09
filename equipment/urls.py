from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    path('equipment/', views.EquipmentListCreateView.as_view(), name='equipment-list-create'),
    path('equipment/<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment-detail'),
    path('equipment/list/', views.EquipmentListView.as_view(), name='equipment-list'),
] 