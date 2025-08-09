from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsTechnicianUser(permissions.BasePermission):
    """
    Custom permission to only allow technician users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_technician


class IsSalesAgentUser(permissions.BasePermission):
    """
    Custom permission to only allow sales agent users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_sales_agent


class IsAdminOrSalesAgent(permissions.BasePermission):
    """
    Custom permission to allow admin or sales agent users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_admin or request.user.is_sales_agent
        )


class IsAssignedTechnician(permissions.BasePermission):
    """
    Custom permission to only allow the assigned technician to modify job/task.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is the assigned technician
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        elif hasattr(obj, 'job') and hasattr(obj.job, 'assigned_to'):
            return obj.job.assigned_to == request.user
        return False


class IsJobCreator(permissions.BasePermission):
    """
    Custom permission to only allow the job creator to modify job.
    """
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user 