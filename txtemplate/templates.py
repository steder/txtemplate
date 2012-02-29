"""
Templates support for Twisted projects
"""

import cStringIO
import os
import string

try:
    from genshi import template as genshitemplate
except ImportError, e:
    genshitemplate = None

try:
    import jinja2
except ImportError, e:
    jinja2 = None

from twisted.internet import defer, reactor
from twisted.python import components
from zope import interface

from txtemplate import clearsilver
from txtemplate import itemplate

CALL_DELAY = 0.001
POPULATE_N_STEPS = 100


class TemplateException(Exception):
    """
    Umbrella exception for all template processing errors

    Anyone interested in catching all template related
    exceptions should simply catch this.
    """
    pass


def registerIfNotRegistered(adapter, from_, to):
    if not components.getAdapterFactory(from_, to, None):
        components.registerAdapter(adapter, from_, to)


class ClearsilverTemplateAdapter(object):
    """
    Adapter that provides itemplate.ITemplate
    """

    interface.implements(itemplate.ITemplate)

    def __init__(self, template):
        self.template = template

    def render_blocking(self, hdf=None, **kwargs):
        hdf = clearsilver.hdfFromKwargs(hdf=hdf, **kwargs)
        cs = clearsilver.CS(hdf)
        cs.parseFile(self.template.template_path)
        result = cs.render()
        return result

    def _prepareHDF(self):
        try:
            hdf = clearsilver.hdfFromKwargs(hdf=self.hdf,
                                        **self.kwargs)
        except Exception, e:
            self._deferred.errback(e)
        else:
            self._deferred.callback(hdf)

    def _failedHDF(self, error):
        print error

    def _rendered(self, hdf):
        cs = clearsilver.CS(hdf)
        cs.parseFile(self.template.template_path)
        result = cs.render()
        return result

    def _failed(self, reason):
        raise TemplateException(
            "Failed to generate template %s because %s"%(
            self.template, reason)
            )

    def render(self, hdf=None, **kwargs):
        self.hdf = hdf
        self.kwargs = kwargs
        self._deferred = defer.Deferred()
        self._deferred.addCallbacks(self._rendered, self._failed)
        reactor.callLater(CALL_DELAY, self._prepareHDF)
        return self._deferred


if clearsilver.CS is not None:
    registerIfNotRegistered(
        ClearsilverTemplateAdapter,
        clearsilver.Template,
        itemplate.ITemplate
    )


class ClearsilverTemplateLoader(object):
    interface.implements(itemplate.ITemplateLoader)

    def __init__(self, path=None):
        self.path = path
        if not self.path:
            self.path = os.curdir

    def load(self, name):
        template_path = os.path.join(self.path, name)
        if not os.path.exists(template_path):
            raise TemplateException("Template %s not found! (expected: %s)"%(name, template_path))
        else:
            template = clearsilver.Template(template_path
                                            )
            return itemplate.ITemplate(template)


if clearsilver.CS is not None:
    registerIfNotRegistered(
        ClearsilverTemplateLoader,
        ClearsilverTemplateLoader,
        itemplate.ITemplateLoader
    )


class GenshiTemplateAdapter(object):
    """
    Adapter that provides itemplate.ITemplate for Genshi Templates
    """

    interface.implements(itemplate.ITemplate)

    def __init__(self, template):
        self._buffer = cStringIO.StringIO()
        self._stream = None
        self.template = template
        self.delayedCall = None

    def _populateBuffer(self, stream, n):
        """
        Iterator that returns N steps of
        the genshi stream.

        Found that performance really sucks for
        n = 1 (0.5 requests/second for the root resources
        versus 80 requests/second for a blocking algorithm).

        Hopefully increasing the number of steps per timeslice will
        significantly improve performance.
        """
        try:
            for x in xrange(n):
                output = stream.next()
                self._buffer.write(output)
        except StopIteration, e:
            self._deferred.callback(None)
        except Exception, e:
            self._deferred.errback(e)
        else:
            self.delayedCall = reactor.callLater(CALL_DELAY, self._populateBuffer, stream, n)

    def _failed(self, reason):
        if self.delayedCall and self.delayedCall.active():
            self.delayedCall.cancel()
        return "Failed to generate template %s because %s"%(self.template, reason)

    def _rendered(self, ignore):
        result = self._buffer.getvalue()
        self._buffer.close()
        self._buffer = None
        if self.delayedCall and self.delayedCall.active():
            self.delayedCall.cancel()
        return result

    def render(self, **kwargs):
        self._stream = self.template.generate(**kwargs)
        self._deferred = defer.Deferred()
        self._deferred.addCallbacks(self._rendered, self._failed)
        s = self._stream.serialize()
        self.delayedCall = reactor.callLater(CALL_DELAY, self._populateBuffer, s, POPULATE_N_STEPS)
        return self._deferred

    def render_blocking(self, **kwargs):
        tmp = self.template.generate(**kwargs)
        return tmp.render()


if genshitemplate is not None:
    registerIfNotRegistered(
        GenshiTemplateAdapter,
        genshitemplate.MarkupTemplate,
        itemplate.ITemplate
    )


class GenshiTemplateLoader(object):
    interface.implements(itemplate.ITemplateLoader)

    def __init__(self, path=None):
        self.path = path
        if not self.path:
            self.path = os.curdir

        self.loader = genshitemplate.TemplateLoader(
            os.path.join(os.path.abspath(self.path)), auto_reload=True
        )

    def load(self, name):
        try:
            template = self.loader.load(name, encoding="UTF-8")
        except genshitemplate.loader.TemplateNotFound:
            raise TemplateException("Template %s not found!"%(name))
        else:
            return itemplate.ITemplate(template)


if genshitemplate is not None:
    registerIfNotRegistered(
        GenshiTemplateLoader,
        genshitemplate.TemplateLoader,
        itemplate.ITemplateLoader
    )


class Jinja2TemplateAdapter(GenshiTemplateAdapter):
    interface.implements(itemplate.ITemplate)

    def render(self, **kwargs):
        iterator = self.template.generate(**kwargs)
        self._deferred = defer.Deferred()
        self._deferred.addCallbacks(self._rendered, self._failed)
        self.delayedCall = reactor.callLater(
            CALL_DELAY, self._populateBuffer,
            iterator, POPULATE_N_STEPS)
        return self._deferred

    def render_blocking(self, **kwargs):
        return self.template.render(**kwargs)


if jinja2 is not None:
    registerIfNotRegistered(
        Jinja2TemplateAdapter,
        jinja2.Template,
        itemplate.ITemplate
    )


class Jinja2TemplateLoader(object):
    interface.implements(itemplate.ITemplateLoader)

    def __init__(self, path):
        self.path = path
        if not self.path:
            self.path = os.curdir

        self.environment = jinja2.Environment()
        self.loader = jinja2.FileSystemLoader(
            os.path.join(os.path.abspath(self.path)), encoding="utf-8"
        )

    def load(self, name):
        try:
            template = self.loader.load(self.environment, name)
        except jinja2.exceptions.TemplateNotFound:
            raise TemplateException("Template %s not found!"%(name))
        else:
            return itemplate.ITemplate(template)


if jinja2 is not None:
    registerIfNotRegistered(
        Jinja2TemplateLoader,
        jinja2.FileSystemLoader,
        itemplate.ITemplateLoader
    )


class StringTemplateAdapter(object):
    """Adapter that provides itemplate.ITemplate for
    Python's standard string.Template.  This provides
    a basic level of functionality without requiring a
    real templating library.
    """
    interface.implements(itemplate.ITemplate)
    def __init__(self, template):
        self.template = template

    def render_blocking(self, **kwargs):
        rendered = self.template.substitute(kwargs)
        return rendered

    def _render(self, kwargs):
        try:
            rendered = self.template.substitute(kwargs)
        except Exception, e:
            self._deferred.errback(e)
        else:
            self._deferred.callback(rendered)

    def _rendered(self, rendered):
        return rendered

    def _failed(self, reason):
        raise TemplateException(
            "Failed to generate template %s because %s"%(
            self.template, reason)
            )

    def render(self, **kwargs):
        self._deferred = defer.Deferred()
        self._deferred.addCallbacks(self._rendered, self._failed)
        reactor.callLater(CALL_DELAY, self._render, kwargs)
        return self._deferred


registerIfNotRegistered(
        StringTemplateAdapter,
        string.Template,
        itemplate.ITemplate
)


class StringTemplateLoader(object):
    interface.implements(itemplate.ITemplateLoader)

    def __init__(self, path=None):
        self.path = path
        if not self.path:
            self.path = os.curdir

    def load(self, name):
        template_path = os.path.join(self.path, name)
        if not os.path.exists(template_path):
            raise TemplateException("Template %s not found! (expected: %s)"%(name, template_path))
        else:
            templateContent = open(template_path, "r").read()
            template = string.Template(templateContent)
            return itemplate.ITemplate(template)

registerIfNotRegistered(
        StringTemplateLoader,
        StringTemplateLoader,
        itemplate.ITemplateLoader
)
