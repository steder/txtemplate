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
 - Jinja2

------------------------------------------
Getting Started
------------------------------------------

All you really need to do to use txTemplate in twisted is:
 - import it
 - create a loader pointed at your template directory
 - load a template with said loader
 - call template.render, attach callbacks to the rendered deferred (if desired) and return the deferred from and of your twisted.web.resource.Resource render_* methods.

Here's a code sample of a Twisted Web resource that uses txTemplate
to render a lovely Genshi template to say Hello World in HTML::

    import os

    from twisted.application import internet
    from twisted.internet import reactor
    from twisted.web import resource
    from twisted.web import server

    import txtemplate


    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "templates")


    class HelloWorld(resource.Resource):
        def __init__(self):
            resource.Resource.__init__(self)
            self.loader = txtemplate.GenshiTemplateLoader(TEMPLATE_DIR)

        def getChild(self, name, request):
            return self

        def render_GET(self, request):
            template_name = "hello.xhtml"
            template = self.loader.load(template_name)
            context = {"greeting": "Hello",
                    "greetee": "World"}

            def cb(content):
                request.write(content)
                request.setResponseCode(200)
                request.finish()

            d = template.render(**context)
            d.addCallback(cb)
            return server.NOT_DONE_YET


    site = server.Site(HelloWorld())
    reactor.listenTCP(8888, site)
    reactor.run()


This example is included in `txtemplate/examples/txweb.py` and the
`root.xhtml` template is in `txtemplate/examples/templates/root.xhtml`.



