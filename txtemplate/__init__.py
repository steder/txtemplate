# __init__.py
"""
txtemplate
=======================

Provides a common twisted-friendly interface for
template systems like:

 - Clearsilver
 - Genshi
 - Jinja2

"""

from .templates import ClearsilverTemplateLoader
from .templates import GenshiTemplateLoader
from .templates import Jinja2TemplateLoader


__all__ = ["ClearsilverTemplateLoader",
           "GenshiTemplateLoader",
           "Jinja2TemplateLoader"]
