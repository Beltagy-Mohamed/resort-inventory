from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)

@register.filter
def percentage(value, arg):
    try:
        value = float(value or 0)
        arg = float(arg or 0)
        if arg == 0:
            return 0
        return round((value / arg) * 100, 1)
    except (ValueError, TypeError):
        return 0
