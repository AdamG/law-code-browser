"""Load the entire US law code into the database.
"""

from optparse import make_option
import re
import os
import string
import tempfile

from django.core.management.base import BaseCommand, NoArgsCommand
from django.db.transaction import commit_on_success

from law_code.models import Section, Code


us_section_rx = re.compile("""
^\- HEAD \-# The header of each... well, header.
.*\n # Get to the next line, when the content starts
\W* # strip the leading whitespace
([\w]+?) # The first group: part, section, title, etc
(?:\-1)? # This is a special case for Title 42, Chapter 77, Subchaper
         # III, Part A-1, which is inconsistently named, and should
         # either be renamed B, or removed entirely.
\.? # Sections are usually abbreviated "Sec." - so, ignore the period
\W # Strop whitespace after the title
([0-9]+[a-z]?) # Each section is ually a number with at most 1 suffix
               # character, or a single character. This matches both.
\.?# Section *numbers* usually have a trailing dot -  "2181."
(?:\- )? # Larger sections (titles, etc) use SECTION X - THE TITLE
\W+ # Force whitespace between section and title
([\r\na-zA-Z,\(\) ]+) # The title of the section
\\r\\n\\r\\n # Two newlines end the title
""", re.VERBOSE|re.MULTILINE)

section_mapping = {
    "sec": Section.SECTION,
    "chapter": Section.CHAPTER,
    "title": Section.TITLE,
    # Usually, eg, "secs 210 to 215: repealed". Exclude for now.
    "secs": None,
    "subchapter": Section.SUBCHAPTER,
    "subpart": Section.SUBPART,
    "part": Section.PART,
    "division": Section.DIVISION,
    }

class Command(BaseCommand):
    help = 'Import a law code.'
    option_list = NoArgsCommand.option_list + (
        make_option('--directory', action='store', dest='directory',
                    help='Use downloaded files (Title_01.txt, etc) in this directory; '
                    'see http://uscode.house.gov/download/ascii.shtml\n'
                    'Otherwise, all the files are downloaded, which will take upwards of an hour.'),
    )
    args = "type(US)"
    def handle(self, **options):
        self.opts = options
        self.load_us_code()

    @commit_on_success
    def _load_us_code_title(self, title_file):
        """
        Load a single US code title file, run a regex over it, and
        build Section objects out of it.

        The execution of this function is broken into two sections:
        Heuristic ordering of section types, determination of a
        promotion, sibling, or drill Section addition, and then
        creation of the Section object.

        Ordering Section Types
        ======================

        The US code does not use consistent ordering. This is just one
        of many beautiful features that makes it a write-only
        document. The Title is the uppermost division, while the
        Section is always, AFAIK, the smallest division. However, the
        divisions bewtween Title and Section do not use consistent
        ordering:

        http://en.wikipedia.org/wiki/United_States_Code#Organization

        Since greater subtypes must always precede lower ones, I
        simply loop through all the sections, and add each new section
        type if it hasn't yet been added to the ordering list.

        Determination of the Parent
        ===========================

        TODO: Rewrite

        """
        print "Starting %r" % title_file
        section_match_groups = us_section_rx.findall(title_file.read())

        # See "Ordering Section Types"
        order = []
        for groups in section_match_groups:
            section = groups[0].lower().strip()
            if section not in order:
                order.append(section)
        print order

        parents = {}
        for sectype in order:
            parents[sectype] = None

        for groups in section_match_groups:

            sectype, number, name = groups
            sectype = sectype.lower().strip()

            # Clear out child types, so they aren't seen as potential parents.
            child_types = order[order.index(sectype):]
            for ct in child_types:
                parents[ct] = None
            parent = None
            potential_parent_types = order[:order.index(sectype)]
            for ppt in potential_parent_types:
                if parents[ppt] is not None:
                    parent = parents[ppt]

            name = name.rstrip("\r")
            assert sectype in section_mapping, sectype
            type = section_mapping[sectype]
            if type is None:
                continue
            kwargs = {
                "code": self.us_code,
                "name": name,
                "number": number,
                "type": type,
                "parent": parent}
            if False:
                parents[sectype] = kwargs
            else:
                sec = Section.objects.create(**kwargs)
                parents[sectype] = sec

    def load_us_code(self):
        self.us_code, created = Code.objects.get_or_create(
            name="US Code", type=Code.COUNTRY)
        if self.opts.get("directory", False):
            base_dir = os.path.abspath(os.path.expanduser(self.opts["directory"]))
            name_fmt = "Title_%s.txt"
            for ii in range(1, 51):
                if ii < 10:
                    str_ii = "0%d" % ii
                else:
                    str_ii = str(ii)
                name = name_fmt % str_ii
                self._load_us_code_title(file(os.path.join(base_dir, name)))
