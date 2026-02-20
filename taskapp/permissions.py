from rest_framework.permissions import BasePermission

from .models import User


class TaskAccessPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method == "DELETE" and user.role == User.Role.CLIENT:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == User.Role.CLIENT:
            return obj.created_by_id == user.id
        return True
