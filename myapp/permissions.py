from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # GET,HEAD,OPTIONS
            if request.method is permissions.SAFE_METHODS:
                return True
            return obj.user_name==request.user
