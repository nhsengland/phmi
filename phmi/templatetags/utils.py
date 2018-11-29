# templatetags file
from django import template
from django.urls import resolve
from django.urls import reverse

register = template.Library()


@register.filter(name="url_name")
def url_name(request):
    return resolve(request.path_info).url_name


@register.inclusion_tag('template_tags/breadcrumbs.html')
def breadcrumbs(breadcrumbs):
    return dict(breadcrumbs=breadcrumbs)