from django import template


register = template.Library()

@register.filter
def add_width(a, b):
    return a+b

