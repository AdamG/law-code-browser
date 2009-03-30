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
        ``order`` variable. If the matched section type is
        ``order[0]``, then .parent is None. (This should happen only
        with Title, and I may special-case it to make sure this is the
        case - haven't decided yet.)

        Otherwise, I find the parent section type with
        ``order[order.index(sectype)-1]``. I then look up into
        ``parents[parent_section_type]``, and use that as
        ``Section.parent``.


        """

        # See "Ordering Section Types"
        section_counts = {}
        section_matches = us_section_rx.find(title_file.read())
        for match in section_matches:
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

        parents = {}
        for sectype in order:
            parents[sectype] = None

        for match in section_matches:
            sectype, number, name = match.groups()
            sectype = sectype.lower()
            number = int(number)
            name = name.rstrip("\r")
            assert sectype in section_mapping, sectype
            if order.index(sectype) == 0:
                parent = None
            else:
                parent_section_type = order[order.index(sectype)-1]
                parent = parents[parent_section_type]
                assert parent is not None
            type = section_mapping[sectype]
            if type is None:
                continue
            kwargs = {
                "code": us_code,
                "name": name,
                "number": number,
                "type": type}
            if True:
                print kwargs
            else:
                Section.objects.create(**kwargs)

    def load_us_code(self):
        self.us_code, created = Code.objects.get_or_create(
            name="US Code", type=Code.COUNTRY)
        if self.opts.get("directory", False):
            base_dir = os.path.abspath(self.opts["directory"])
            name_fmt = "Title_%s.txt"
            for ii in range(1, 51):
                if ii < 10:
                    str_ii = "0%d" % ii
                else:
                    str_ii = str(ii)
                name = name_fmt % str_ii
            self._load_us_code_title(file(os.path.join(base_dir, name)))
