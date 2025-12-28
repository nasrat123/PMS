from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Custom template filter that checks if a user belongs to a specific group.
    Usage in template: {% if user|has_group:"Doctor" %}
    """
    return user.groups.filter(name=group_name).exists()
