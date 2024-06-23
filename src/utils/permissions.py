from rest_framework.permissions import BasePermission


class IsInternal(BasePermission):
    """
    Allows access only internal permissions
    """

    def has_permission(self, request, view):
        return getattr(request, "is_internal", False)