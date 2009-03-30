"""Load the entire US law code into the database.
"""

from optparse import make_option
import re
import os
import string
import tempfile

from django.core.management.base import BaseCommand, NoArgsCommand

from law_code.models import Section, Code


us_section_rx = re.compile("HEAD.*\n.*?\W*([\w ]+)?\.? (\w+)\.? (?:\- )?(.*?)\W*\n")
section_mapping = {
    "sec": Section.SECTION,
    "chapter": Section.CHAPTER,
    "title": Section.TITLE,
    # Usually, eg, "secs 210 to 215: repealed"
    "secs": None}

class Command(BaseCommand):
    help = 'Import a law code.'
    option_list = NoArgsCommand.option_list + (
        make_option('--directory', action='store_true', dest='directory',
                    help='Use downloaded files (Title_01.txt, etc) in this directory; '
                    'see http://uscode.house.gov/download/ascii.shtml\n'
                    'Otherwise, all the files are downloaded, which will take upwards of an hour.'),
    )
    args = "type(US)"
    def handle(self, type, **options):
        self.opts = options
        if type == "US":
            self.load_us_code()


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

        I originally planned to special-case the ordering, and then
        handle promotion and drilling programmatically, however,
        manually handling fifty Titles doesn't seem appealing.

        Instead, I assume that there will always be more of each type
        of subsection than their is of the parent section. For
        example, each title will have only 1 Title, and, for example,
        4 Chapters, and 30 Sections. The first part of this function
        counts, in a dictionary, the number of each type of
        subsection. It then orders them from the smallest number to
        highest number, and creates the ``order`` variable which is
        referenced later on.

        We now enter the loop ``rx.finditer`` loop.

        Determination of the Parent
        ===========================

        Determining the parent makes use of the now-available
        ``order`` variable. For each match, I compare if the new
        ``sectype`` with ``last_sectype``.


        """

        # First, figure out what the ordering of this title is (they
        # are *not* consistent) by counting the type of each
        # section. The fewer there are of a section, the higher in the
        # the section heirarchy they are.
        section_counts = {}
        for match in us_section_rx.finditer(title_file.read()):
            section = m.groups()[0].lower()
            assert section in section_mapping, section
            if section in section_counts:
                section_counts[section] += 1
            else:
                section_counts[section] = 1
        swapped_tuples = [(t[1], t[0]) for t in section_counts.iteritems()]
        swapped_tuples.sort()
        # This is the final heirarchy order
        order = [t[1] for t in swapped_tuples]

        title_file.seek(0)

        # Now I build a dictionary of the last parent of each type in
        # ``order``. When a sectype promotion is found (see below), I
        # look inside this dictionary to find what object to set as
        # ``Section.parent``.
        parents = {}
        for sectype in order:
            parents[sectype] = None

        # Now, we start inserting Section objects. In most cases, for
        # example, a Section.SECTION following a Section.SECTION, we
        # simply use 'parent'.  There are two special cases, which I
        # will call "drill" and "promote". 
        #
        # Drilling

        parent = None
        previous_sectype = None
        for match in us_section_rx.finditer(title_file.read()):
            if previous_sectype
            sectype, number, name = match.groups()
            number = int(number)
            name = name.rstrip("\r")
            assert sectype.lower() in section_mapping, sectype
            type = section_mapping[sectype.lower()]
            if type is None:
                continue
            Section.objects.create(
                code=us_code,
                name=name,
                number=number,
                type=type)
            previous_sectype = sectype

    def load_us_code(self):
        self.us_code, created = Code.objects.get_or_create(
            name="US Code", type=Code.COUNTRY)
        if self.opts.get("directory", False):
            self.opts["directory"]





