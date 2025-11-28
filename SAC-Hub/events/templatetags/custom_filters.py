from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    """Check if user has a specific role"""
    if not hasattr(user, 'roles') or not user.roles:
        return False
    return role_name in user.roles

@register.filter
def subtract(value, arg):
    """Subtract the argument from the value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def is_event_organizer(user, event):
    """Check if the user is an organizer OR a club coordinator for the event."""
    if not user.is_authenticated:
        return False
    
    # 1. Event organizers (M2M)
    if event.organizers.filter(id=user.id).exists():
        return True

    # 2. Club coordinators (M2M)
    if event.club and event.club.coordinators.filter(id=user.id).exists():
        return True

    # 3. Event creator
    if event.created_by and event.created_by.id == user.id:
        return True

    return False

@register.filter
def split(value, separator=','):
    """
    Splits a string by the given separator.
    Usage in template: {{ "a,b,c"|split:"," }}
    """
    if value:
        return value.split(separator)
    return []