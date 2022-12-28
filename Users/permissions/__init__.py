from rest_framework.permissions import BasePermission


class IsUserCompanyAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            hasattr(request.user, 'user') and
            hasattr(request.user, 'company') and
            request.user.user.is_active and
            request.user.company.is_active
        )
