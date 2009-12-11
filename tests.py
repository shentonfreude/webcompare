import unittest
import webcompare

class TestWebCompare(unittest.TestCase):

    def setUp(self):
        self.walker = webcompare.Walker("http://nasa.gov", "http://nasa.gov") # lame

    
    def test___init__(self):
        self.assertEquals(self.walker.origin_url_base, "http://nasa.gov")
        self.assertEquals(self.walker.target_url_base, "http://nasa.gov")
        self.assertEquals(self.walker.target_url_parts.scheme, "http")

    def test_fetch(self):
        content = self.walker._fetch_url("http://google.com")
        self.assert_("Feeling Lucky" in content)
        
        

if __name__ == '__main__':
    unittest.main()

