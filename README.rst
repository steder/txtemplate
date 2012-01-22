=================================
txTemplate
=================================

txTemplate provides adapters for a few popular template engines
to make them easily callable and usable within Twisted Web.

txTemplate uses zope.interface to provide a consistent
loader and template interface for every template engine.

------------------------------------------
Supported Template Engines
------------------------------------------

 - ClearSilver
 - Genshi

Jinja2 support coming soon!

------------------------------------------
Getting Started
------------------------------------------

All you really need to do to use txTemplate in twisted is:
 - import it
 - create a loader pointed at your template directory
 - load a template with said loader
 - call template.render, attach callbacks to the rendered deferred (if desired) and return the deferred from and of your twisted.web.resource.Resource render_* methods.

Here's a code sample of a Twisted Web resource that uses txTemplate
to render a lovely Genshi template to say Hello World in HTML.

.. code::
    from twisted.web import resource
    import txtemplate

   TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

    class HelloWorld(resource.Resource):
        def __init__(self):
            self.loader = txtemplate.GenshiTemplateLoader(TEMPLATE_DIR)

        def render_GET(self):
            template_name = "hello.xhtml"
            template = self.loader.load(template_name)
            context = {"greeting": "Hello",
                              "greetee": "World"}
            d = template.render(context)
            return d


