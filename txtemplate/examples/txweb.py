"""
Twisted Web example using txTemplate.
"""

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


