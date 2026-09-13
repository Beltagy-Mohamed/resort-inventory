from django import template

register = template.Library()

@register.filter
def humanize_arabic(value):
    """
    تحويل الأرقام الكبيرة إلى صيغة عربية كاملة:
    1,500,000 => "1 مليون 500 ألف"
    2,300,000,000 => "2 مليار 300 مليون"
    """
    try:
        value = int(float(value))
    except (ValueError, TypeError):
        return value

    if value == 0:
        return "0"

    parts = []

    if value >= 1_000_000_000:
        billions = value // 1_000_000_000
        parts.append(f"{billions} مليار")
        value %= 1_000_000_000

    if value >= 1_000_000:
        millions = value // 1_000_000
        parts.append(f"{millions} مليون")
        value %= 1_000_000

    if value >= 1_000:
        thousands = value // 1_000
        parts.append(f"{thousands} ألف")
        value %= 1_000

    if value > 0:
        parts.append(f"{value:,}")

    return " ".join(parts)
