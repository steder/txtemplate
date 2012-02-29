"""

Examples of using the twisted component registry to
lookup the appropriate template loader.

"""


from twisted.trial import unittest

from txtemplate import clearsilver
from txtemplate.itemplate import ITemplate
from txtemplate import templates


class TestIlookupClearsilver(unittest.TestCase):
    if clearsilver.CS is None:
        skip = "Skipping becasue clearsilver templates are not installed"

    def test_clearsilver(self):
        it = ITemplate(clearsilver.Template("foo"))
        self.assertTrue(it is not None)
        self.assertTrue(ITemplate.providedBy(it))


class TestILookupGenshi(unittest.TestCase):
    """Given a template I should be able to
    get an ITemplate adapter for that template that
    supports the necessary interface.

    """
    if templates.genshitemplate is None:
        skip = "Skipping because genshi templates are not installed"

    def test_genshitemplate(self):
        it = ITemplate(templates.genshitemplate.MarkupTemplate("<html></html>"))
        self.assertTrue(it is not None)
        self.assertTrue(ITemplate.providedBy(it))


class TestILookupJinja2(unittest.TestCase):
    """Given a template I should be able to
    get an ITemplate adapter for that template that
    supports the necessary interface.

    """
    if templates.jinja2 is None:
        skip = "Skipping because jinja2 templates are not installed"

    def test_jinja2template(self):
        it = ITemplate(templates.jinja2.Template("<html></html>"))
        self.assertTrue(it is not None)
        self.assertTrue(ITemplate.providedBy(it))



