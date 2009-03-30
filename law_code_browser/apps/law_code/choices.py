class Choices(object):
    """Takes tuples of (char, attr, display).

    For example::

        GENDER_CHOICES = Choices(
            ("m", "MALE", "Male"),
            ("f", "FEMALE", "Female")
            )

    You can now 'apply' it to a model like so::

        class Person(models.Model):
            gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
        GENDER_CHOICES.apply_to(Person)

    Which makes the attributes available on Person::

        assert 'm' == Person.MALE
        assert 'f' == Person.FEMALE

    """
    def __init__(self, *choices):
        self.choices = choices

    def __iter__(self):
        for choice in self.choices:
            yield choice[0], choice[2]

    def apply_to(self, obj):
        for value, attr, display in self.choices:
            setattr(obj, attr, value)


CODE_TYPE_CHOICES = Choices(
    ("country", "COUNTRY", "National"),
    ("state", "STATE", "State"),
)

SECTION_TYPE_CHOICES = Choices(
    ("title", "TITLE", "Title"),
    ("subtitle", "SUBTITLE", "Subtitle"),
    ("chapter", "CHAPTER", "Chapter"),
    ("subchapter", "SUBCHAPTER", "Subchapter"),
    ("part", "PART", "Part"),
    ("subpart", "SUBPART", "Subpart"),
    ("section", "SECTION", "Section"),
    ("subsection", "SUBSECTION", "Subsection"),
    ("paragraph", "PARAGRAPH", "Paragraph"),
    ("subparagraph", "SUBPARAGRAPH", "Subparagraph"),
    ("clause", "CLAUSE", "Clause"),
    ("subclause", "SUBCLAUSE", "Subclause"),
)
