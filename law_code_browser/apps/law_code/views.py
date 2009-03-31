from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from law_code import models


def view_code(request, code_id, template="law_code/code_index.html"):
    code = get_object_or_404(models.Code.objects.filter(public=True), id=int(code_id))
    return direct_to_template(request, template, {"code": code})


def view_section(request, code_id, section_string):
    """URL resolution here needs to be able to handle an arbitrary
    depth of sections.

    To do so, everything after the code_id is captured and passed as
    section_string. Then, I split on '/', and keep drilling down to
    the correct Section.

    """
    code = get_object_or_404(models.Code.objects.filter(public=True), id=int(code_id))
    section_parts = section_string.split('/')
    if not section_parts:
        raise Http404("No section segment found")
    root_section_number = section_parts.pop(0)
    root_section = get_object_or_404(code.sections.filter(parent=None), current_version=True, number=root_section_number)
    parent = root_section
    if not section_parts:
        node = root_section
    for part in section_parts:
        node = parent.get_children().get(number=part)
        parent = node

    return direct_to_template(
        request, "law_code/code_section.html",
        {"section": node})
