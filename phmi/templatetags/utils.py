# templatetags file
from django import template
from django.urls import resolve
from django.utils.safestring import mark_safe
import more_itertools

register = template.Library()


@register.filter
def url_name(request):
    return resolve(request.path_info).url_name

@register.filter(is_safe=True)
def structure_name(name):
  return mark_safe("<br/>(".join(name.split("(")))

@register.filter
def chuncked(some_list, amount):
  return more_itertools.chunked(some_list, amount)

@register.filter
def legal_justifications(activity, org_type):
    from phmi.models import LegalJustification, LawfulBasis

    specific_lj = LegalJustification.objects.filter(
        activity=activity
    ).filter(org_type=org_type).filter(is_specific=True)
    general_lj = LegalJustification.objects.filter(
        activity=activity
    ).filter(org_type=org_type).filter(is_specific=False)

    specific_lb = list(LawfulBasis.objects.filter(legal_justifications__in=specific_lj))
    for lb in specific_lb:
        lb.is_specific = True
        is_generic = False

    general_lb = list(LawfulBasis.objects.filter(legal_justifications__in=general_lj))
    for lb in general_lb:
        lb.is_specific = False
        lb.is_generic = True

    return specific_lb + general_lb


@register.inclusion_tag("template_tags/breadcrumbs.html")
def breadcrumbs(breadcrumbs):
    return dict(breadcrumbs=breadcrumbs)
