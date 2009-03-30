"""Models for the law code

See:
 * http://en.wikipedia.org/wiki/United_States_Code#Organization

There is no common organization for the titles of the US Code. As a
result, each level of arbitrarily-nested sections must be aware of
it's own label.

I currently do *not* know if section labelling *within* each title is
consistent. If so, it would be possible to somehow make each title
aware of it's own organization, then just use a tree of objects.

"""
from django.core.urlresolvers import reverse
from django.db import models

import mptt

from law_code import choices


class Code(models.Model):
    "A Law Code, eg, the US Law Code."
    name = models.CharField(max_length = 127)
    type = models.CharField(max_length=127, choices=choices.CODE_TYPE_CHOICES)
    public = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "law_code_code"

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<law_code.Code %s>" % unicode(self)

    def get_absolute_url(self):
        return reverse("view-law-code", args=[self.id])

    def get_top_level_sections(self):
        "Return the top-level sections associated with this Code"
        return self.sections.filter(parent=None, current_version=True)\
            .order_by("number")

choices.CODE_TYPE_CHOICES.apply_to(Code)


class Section(models.Model):
    """A section of a Code.

    This does *not* represent, for example, a section of the US
    Code. Rather, it may represent a section, and it may represent
    a title, section, chapter, part, paragraph, clause, etc etc.

    A sample structure:

        type == TITLE, endpoint == False
            type == SECTION, endpoint == False, order = 1
                type == PARAGRAPH, endpoint == True, order = 1, content = "legalese"
                type == PARAGRAPH, endpoint == True, order = 2, content = "more legalese"
            type == SECTION, endpoint == False, order = 2

    """
    code = models.ForeignKey(Code, related_name="sections")
    name = models.TextField()
    type = models.CharField(max_length=127, choices=choices.SECTION_TYPE_CHOICES)
    parent = models.ForeignKey('self', null=True)
    content = models.TextField(null=True, blank=True)
    # 1-indexed, as it's used in combination with .type to generate a header
    number = models.PositiveIntegerField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # Set to False when changing the content
    current_version = models.BooleanField(default=True)

    class Meta:
        db_table = "law_code_section"

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "<law_code.Section(%s) %s>" % (
            self.get_type_display(), unicode(self))

    def get_absolute_url(self):
        section_parts = [str(sec.number) for sec in self.get_ancestors()] + [str(self.number)]
        section_url_fragment = '/'.join(section_parts)
        return reverse("view-code-section",
                       args=[self.code.id, section_url_fragment])

mptt.register(Section)
choices.SECTION_TYPE_CHOICES.apply_to(Section)

