from django.db import models


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
