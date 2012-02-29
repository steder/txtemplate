from twisted.internet import defer, reactor
from twisted.trial import unittest
from twisted.internet import base
from twisted.python import failure, filepath
base.DelayedCall.debug = True

from txtemplate import templates
from txtemplate import clearsilver

TEMPLATE_DIR = filepath.FilePath(__file__
                                 ).parent().parent().child("templates").path


class TestClearsilverTemplates(unittest.TestCase):
    if clearsilver.CS is None:
        skip = "Skipping Clearsilver tests because Clearsilver is not installed."

    def setUp(self):
        self.c = {"request":"foo",
                  "segments":["hello","world"],
                  "message":"error message",
                  }

        self.loader = templates.ClearsilverTemplateLoader(
            TEMPLATE_DIR
            )

    class TestClass(object):
        someProperty = "Some Property Value"
        def __str__(self):
            return self.someProperty

    def test_loader_failure(self):
        self.assertRaises(templates.TemplateException, self.loader.load, "filethatdoesnotexist.cst")

    def test_loader_success(self):
        template = self.loader.load("test.cst")
        self.assertTrue(isinstance(template, templates.ClearsilverTemplateAdapter))

    def test_render_blocking(self):
        template = self.loader.load("test.cst")
        xhtml = template.render_blocking(**self.c)
        self.assertTrue(xhtml.find("foo") !=-1)

    def test_render_blocking_list(self):
        template = self.loader.load("test.cst")
        xhtml = template.render_blocking(**self.c)
        self.assertTrue(xhtml.find("<div>hello</div>") !=-1)

    def test_render_blocking_list_objects(self):
        template = self.loader.load("test.cst")
        self.c["segments"][0] = self.TestClass()
        xhtml = template.render_blocking(**self.c)
        self.assertTrue(xhtml.find("<div>Some Property Value</div>") !=-1)

    def test_render_blocking_list_of_lists(self):
        template = self.loader.load("test.cst")
        self.c["segments"][0] = ["h","e","l","l","o"]
        xhtml = template.render_blocking(**self.c)
        self.assertTrue(xhtml.find("<p>h</p>") !=-1)

    def test_render_blocking_dict(self):
        template = self.loader.load("test.cst")
        self.c['dict'] = {"test":"1 key",
                          "test_list":[1,2,3],
                          "test_dict":{"nested":"2 key",
                                       "nested_list":[4,5,6],
                                       },
                          }
        xhtml = template.render_blocking(**self.c)
        self.assertTrue(xhtml.find("<p>1 key</p>") !=-1)
        self.assertTrue(xhtml.find("<p>2 key</p>") !=-1)

    def test_render_blocking_hdf(self):
        template = self.loader.load("test.cst")
        hdf = clearsilver.hdfFromKwargs(**self.c)
        xhtml = template.render_blocking(hdf=hdf)
        self.assertTrue(xhtml.find("foo") !=-1)

    def _success(self, result):
        self.assertTrue(result.find("</html>")!=-1)

    def test_render_success(self):
        template = self.loader.load("test.cst")
        d = template.render(**self.c)
        d.addCallback(self._success)


class TestGenshiTemplates(unittest.TestCase):
    if templates.genshitemplate is None:
        skip = "Skipping Genshi tests because genshi is not installed."

    def setUp(self):
        self.c = {"request":"foo",
                  "segments":["hello","world"],
                  "message":"error message"
                  }
        self.loader = templates.GenshiTemplateLoader(TEMPLATE_DIR)

    def test_loader_failure(self):
        self.assertRaises(templates.TemplateException, self.loader.load, "filethatdoesnotexist.xhtml")

    def test_loader_success(self):
        template = self.loader.load("error.xhtml")
        self.assertTrue(isinstance(template, templates.GenshiTemplateAdapter))

    def test_render_blocking(self):
        template = self.loader.load("error.xhtml")
        xhtml = template.render_blocking(**self.c)
        self.assertTrue(xhtml.find("foo") !=-1)

    def test_failed(self):
        template = self.loader.load("error.xhtml")
        #self.assertRaises(templates.TemplateException, template._failed, failure.Failure(ValueError))
        f = failure.Failure(ValueError)
        errorMessage = "Failed to generate template"
        self.assertTrue(errorMessage in template._failed(f))

    def test_rendered(self):
        template = self.loader.load("error.xhtml")
        template._buffer.write("Some string o' crap!")
        result = template._rendered(None)
        self.assertEqual(result, "Some string o' crap!")

    def _success(self, result):
        self.assertTrue(result.find("</html>")!=-1)

    def test_populateBuffer(self):
        template = self.loader.load("error.xhtml")
        template._deferred = defer.Deferred()
        template._deferred.addCallbacks(template._rendered, template._failed)
        template._deferred.addCallback(self._success)
        template._stream = template.template.generate(**self.c)
        s = template._stream.serialize()
        reactor.callLater(0.01, template._populateBuffer, s, templates.POPULATE_N_STEPS)
        return template._deferred

    def test_render(self):
        template = self.loader.load("error.xhtml")
        d = template.render(**self.c)
        d.addCallback(self._success)
        return d


class TestJinja2Templates(unittest.TestCase):
    if templates.jinja2 is None:
        skip = "Skipping Jinja2 tests because jinja2 is not installed."

    def setUp(self):
        self.c = {"request":"foo",
                  "segments":["hello","world"],
                  "message":"error message"
                  }
        self.loader = templates.Jinja2TemplateLoader(TEMPLATE_DIR)

    def test_loader_failure(self):
        self.assertRaises(templates.TemplateException, self.loader.load, "filethatdoesnotexist.jinja2")

    def test_loader_success(self):
        template = self.loader.load("test.jinja2")
        self.assertTrue(isinstance(template, templates.Jinja2TemplateAdapter))

    def test_render_blocking(self):
        template = self.loader.load("test.jinja2")
        html = template.render_blocking(**self.c)
        self.assertTrue(html.find("foo") !=-1)

    def _success(self, result):
        self.assertTrue(result.find("foo")!=-1)
    def test_render(self):
        template = self.loader.load("test.jinja2")
        d = template.render(**self.c)
        d.addCallback(self._success)
        return d


class TestStringTemplates(unittest.TestCase):
    def setUp(self):
        self.c = {"request":"foo",
                  "segments":["hello","world"],
                  "message":"error message",
                  }

        self.loader = templates.StringTemplateLoader(
            TEMPLATE_DIR
            )

    class TestClass(object):
        someProperty = "Some Property Value"
        def __str__(self):
            return self.someProperty

    def test_loader_failure(self):
        self.assertRaises(templates.TemplateException, self.loader.load, "filethatdoesnotexist.cst")

    def test_loader_success(self):
        template = self.loader.load("test.txt")
        self.assertTrue(isinstance(template, templates.StringTemplateAdapter))

    def test_render_blocking(self):
        template = self.loader.load("test.txt")
        xhtml = template.render_blocking(**self.c)
        self.assertTrue(xhtml.find("foo") !=-1)

    def _success(self, result):
        self.assertTrue(result.find("</html>")!=-1)

    def test_render_success(self):
        template = self.loader.load("test.txt")
        d = template.render(**self.c)
        d.addCallback(self._success)

