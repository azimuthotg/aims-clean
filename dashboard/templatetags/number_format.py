from django import template
from django.utils.safestring import mark_safe
import locale

register = template.Library()

@register.filter
def format_number(value):
    """
    Format number with comma separator for thousands
    Usage: {{ number|format_number }}
    """
    try:
        if value is None:
            return ''
        
        # Convert to int or float
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    return value
        
        # Format with comma separator
        if isinstance(value, (int, float)):
            return f"{value:,}"
        
        return value
    except (ValueError, TypeError):
        return value

@register.filter
def format_number_th(value):
    """
    Format number with Thai locale
    Usage: {{ number|format_number_th }}
    """
    try:
        if value is None:
            return ''
        
        # Convert to number
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    return value
        
        # Format with Thai locale (comma separator)
        if isinstance(value, (int, float)):
            return f"{value:,}"
        
        return value
    except (ValueError, TypeError):
        return value

@register.filter
def format_compact(value):
    """
    Format number in compact form (K, M, B)
    Usage: {{ number|format_compact }}
    """
    try:
        if value is None:
            return ''
        
        # Convert to number
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    return value
        
        if isinstance(value, (int, float)):
            if value >= 1_000_000_000:
                return f"{value/1_000_000_000:.1f}B"
            elif value >= 1_000_000:
                return f"{value/1_000_000:.1f}M"
            elif value >= 1_000:
                return f"{value/1_000:.1f}K"
            else:
                return f"{value:,}"
        
        return value
    except (ValueError, TypeError):
        return value