from django.contrib.auth.decorators import user_passes_test

def role_required(*role_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_roles(u):
        if u.is_authenticated():
            if bool(u.profile.roles.filter(name__in=role_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_roles)