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