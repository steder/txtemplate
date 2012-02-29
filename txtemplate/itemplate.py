"""itemplate.py

Interfaces for the txTemplate
"""

from zope import interface


class ITemplateLoader(interface.Interface):
    """
    Template loaders simply take a template name and return an instance of a
    template object.

    Arguably this would be better as a simple IFile adapter.
    """

    def load(name):
        """
        Load the template from a unique identifier, usually the file name
        without the path.  The loader itself knows the path to the template.
        """


class ITemplate(interface.Interface):
    """
    A document, used as a pattern for generating content via the
    insertion of data into predefined locations within the document.
    """

    def render(**kwargs):
        """
        Return an instance of twisted.internet.defer.Deferred, which will fire
        with the rendered string, or, in the case of an error, an instance of
        txtemplate.templates.TemplateException.

        Examples:
            def failureFunction(reason):
                print reason

            def successFunction(renderedString):
                print renderedString

            data = {'key1': value1, 'key2': value2}
            d1 = template.render(**data)
            d1.addCallbacks(successFunction, failureFunction)

            d2 = template.render(key1=value1, key2=value2)
            d2.addCallbacks(successFunction, failureFunction)
        """

    def render_blocking(**kwargs):
        """
        Render my content as a string, using the key-value pairs provided as
        arguments to this method.

        Examples:
            data = {'key1': value1, 'key2': value2}
            s1 = template.render_blocking(**data)

            s2 = template.render_blocking(key1=value1, key2=value2)
        """



