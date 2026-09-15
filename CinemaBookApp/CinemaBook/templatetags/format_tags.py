from django import template

register = template.Library()

@register.filter(name='intdot')
def intdot(value):
    """
    Format a number with dots as thousand separators (e.g., 1000000 -> 1.000.000)
    """
    if value is None or value == '':
        return '0'
    try:
        val = float(value)
        return f"{val:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)

@register.filter(name='currency_vnd')
def currency_vnd(value):
    """
    Format a number with dots as thousand separators and append VNĐ (e.g., 1000000 -> 1.000.000 VNĐ)
    """
    return f"{intdot(value)} VNĐ"
