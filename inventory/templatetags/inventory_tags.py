from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.filter
def humanize_arabic(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value
        
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f} {_('Billion')}".replace('.00', '')
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f} {_('Million')}".replace('.00', '')
    elif value >= 1_000:
        return f"{value / 1_000:.2f} {_('Thousand')}".replace('.00', '')
    else:
        return f"{value:,.0f}"
