import unittest
import webcompare

class TestWebCompare(unittest.TestCase):

    def setUp(self):
        self.walker = webcompare.Walker("http://example.net",
                                        "http://example.org")

    def test___init__(self):
        self.assertEquals(self.walker.origin_url_base, "http://example.net")
        self.assertEquals(self.walker.target_url_base, "http://example.org")
        self.assertEquals(self.walker.target_url_parts.scheme, "http")

    def test_walker_texas_ranger(self):
        self.assert_("wannabe military type" in self.walker._texas_ranger())

    def test_fetch(self):
        content = self.walker._fetch_url("http://google.com")
        self.assert_("Feeling Lucky" in content)
        
        
    def test__get_urls_abs(self):
        urls = self.walker._get_urls('<body><a href="http://example.com/foo">foo</a></body>',
                                     base_href="IGNORED")
        urllist = list(urls)
        self.assertEquals(len(urllist), 1)
        self.assertEquals(urllist[0][2], "http://example.com/foo")

    def test__get_urls_based(self):
        urls = self.walker._get_urls('<body><a href="/bar">bar</a></body>',
                                     base_href="http://example.com")
        urllist = list(urls)
        self.assertEquals(len(urllist), 1)
        self.assertEquals(urllist[0][2], "http://example.com/bar")

if __name__ == '__main__':
    unittest.main()

