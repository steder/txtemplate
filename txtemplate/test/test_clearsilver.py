from twisted.trial import unittest
from twisted.internet import base
base.DelayedCall.debug = True

from txtemplate.templates import clearsilver

class TestClearsilver(unittest.TestCase):
    if clearsilver.CS is None:
        skip = "Skipping Clearsilver tests because Clearsilver is not installed."

    def setUp(self):
        self.hdf = clearsilver.HDF()

    def test_hdf_get_set_Value(self):
        page = "subcontract listing"
        self.hdf.setValue("page", page)
        self.assertEqual(page, self.hdf.getValue("page",""))
        
    
