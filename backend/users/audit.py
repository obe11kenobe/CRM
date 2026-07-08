from .models import AuditLogEntry


def log_action(user, action, obj, details=''):
    AuditLogEntry.objects.create(
        user=user if getattr(user, 'is_authenticated', False) else None,
        action=action,
        model_name=obj.__class__.__name__,
        object_id=str(obj.pk),
        object_repr=str(obj)[:200],
        details=details,
    )
