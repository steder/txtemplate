#-*- test-case-name: txtemplate.test.test_clearsilver -*-
"""
Clearsilver library integration point

Handles imports of clearsilver modules and
provides helper routines to handle common
operations on hdf objects.
"""

try:
    import neo_cgi # neo_cgi must be imported before neo_cs or neo_util
    import neo_cs
    from neo_cs import CS
    import neo_util
    from neo_util import HDF
except ImportError, e:
    neo_cgi, neo_cs, neo_util, CS, HDF = None, None, None, None, None


class Template(object):
    def __init__(self, template_path):
        self.template_path = template_path



def hdfFromKwargs(hdf=None, **kwargs):
    """If given an instance that has toHDF() method that method is invoked to get that object's HDF representation"""
    if not hdf:
        hdf = HDF()
    for key, value in kwargs.iteritems():
        if isinstance(value, dict):
            #print "dict:",value
            for k,v in value.iteritems():
                dkey = "%s.%s"%(key,k)
                #print "k,v,dkey:",k,v,dkey
                args = {dkey:v}
                hdfFromKwargs(hdf=hdf, **args)
        elif isinstance(value, (list, tuple)):
            #print "list:",value
            for i, item in enumerate(value):
                ikey = "%s.%s"%(key,i)
                #print "i,item:",i,item, ikey
                if isinstance(item, (list, tuple)):
                    args = {ikey:item}
                    hdfFromKwargs(hdf=hdf, **args)
                elif isinstance(item, dict):
                    args = {ikey:item}
                    hdfFromKwargs(hdf=hdf, **args)
                elif getattr(item, "HDF_ATTRIBUTES", False):
                    attrs = {}
                    for attr in item.HDF_ATTRIBUTES:
                        attrs[attr] = getattr(item, attr, "")
                    hdfFromKwargs(hdf=hdf, **{ikey:attrs})
                else:
                    hdf.setValue(ikey, str(item))
        elif getattr(value, "HDF_ATTRIBUTES", False):
            attrs = {}
            for attr in value.HDF_ATTRIBUTES:
                attrs[attr] = getattr(value, attr, "")
            hdfFromKwargs(hdf=hdf, **{key:attrs})
        else:
            hdf.setValue(key, str(value))
    #print "HDF:",hdf.dump()
    return hdf

