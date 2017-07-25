from urllib.parse import urlencode
from django import template


register = template.Library()


@register.filter
def get_type(value):
    return value.__class__.__name__


@register.simple_tag(takes_context=True)
def qstring_replace(context, **kwargs):
    query_string = context['request'].GET.dict()
    query_string.update(kwargs)
    return urlencode(query_string)