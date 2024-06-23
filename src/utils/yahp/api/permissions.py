from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.permissions import AllowAny, BasePermission

from utils.yahp.params import parse_bool


User = get_user_model()

def get_active_user(tenant_id):
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get("_auth_user_id", None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list, tenant_id=tenant_id).first()


class DevAuthMixin:
    """
    Mixin to apply for API views where you would like to circumvent standard permissions
    during development.

    Make sure the mixin is applied first, example:
        class SomeView(DevAuthMixin, APIView):
    """ 
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Check if settings is configured to development
        if settings.DEV_AUTH:
            # Assign random active user with same tenant
            self.request.user = get_active_user(tenant_id=self.request.tenant_id)
            # AllowAny permissions
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]


class UserTenantPermission(BasePermission):
    """
    Permissions Class to validate Request tenant/client is same as the authenticated user.

    Example
    ---------
    permission_classes = [IsAuthenticated, UserTenantPermission]

    """

    message = "Incorrect client code provided"

    def has_permission(self, request, view):
        ## Check for cross tenant requests
        if request.tenant_id != request.user.tenant_id:
            return False

        # Otherwise return valid request
        return True


class UserTenantExternalPermission(BasePermission):
    """
    Permissions Class to validate Request tenant/client is same as the authenticated user.

    Example
    ---------
    permission_classes = [IsAuthenticated, UserTenantPermission]

    """

    message = "Incorrect client code provided"

    def has_permission(self, request, view):
        ## Check for cross tenant requests
        if request.tenant_id != request.user.tenant_id:
            return False

        if hasattr(view, "internal"):
            if view.internal & parse_bool(request.data.get("internal", False)):
                return True

        ## Validate User is granted API Access and 
        if not request.user.api_access:
            self.message = "User not authorized for API access"
            return False
        ## Otherwise return valid request
        return True