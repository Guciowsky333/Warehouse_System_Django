from rest_framework import permissions

class IsForemanOrHigher(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'foreman' or request.user.role == 'manager'