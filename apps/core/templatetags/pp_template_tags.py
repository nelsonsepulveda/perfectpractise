from django.template import Library
from django.urls import resolve

register = Library()


@register.filter
def ifinlist(value, val_list):
    return True if value in val_list else False


@register.simple_tag
def nav_active(request, url):
    """
    In template: {% nav_active request "url_name_here" %}
    """
    url_name = resolve(request.path).url_name

    if url_name == url:
        return "active"
    return ""
