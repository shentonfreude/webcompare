import unittest

class TestWebCompare(unittest.TestCase):

    def setUp(self):
        from webcompare import Walker
        self.walker = Walker("http://origin.int", "http://target.int")

    def test___init__(self):
        self.assertEquals(self.walker.origin_url_base, "http://origin.int")
        self.assertEquals(self.walker.target_url_base, "http://target.int")
        self.assertEquals(self.walker.target_url_parts.scheme, "http")

    def test_walker_texas_ranger(self):
        self.assert_("wannabe military type" in self.walker._texas_ranger())

    def test__fetch_url_content(self):
        content = self.walker._fetch_url_content("http://google.com")
        self.assert_("Feeling Lucky" in content)
        
    def test__get_target_url_abs(self):
        turl = self.walker._get_target_url("http://origin.int/foo/bar/stuff.png")
        self.assertEquals(turl, "http://target.int/foo/bar/stuff.png")

    def test__get_target_url_rel(self):
        turl = self.walker._get_target_url("/foo/bar/stuff.png")
        self.assertEquals(turl, "http://target.int/foo/bar/stuff.png")

    def test__is_within_origin(self):
        self.assertTrue(self.walker._is_within_origin("http://origin.int/some/where"))

        
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

    def test_add_comparator(self):
        def bogus_comparator(self):
            pass
        self.walker.add_comparator(bogus_comparator)
        self.assertEquals(self.walker.comparators[-1], bogus_comparator)

class TestNormalizer(unittest.TestCase):

    def setUp(self):
        pass

    def test___init__(self):
        from webcompare import Normalizer
        normalizer = Normalizer("<html><head><title>TITLE</title></head><body><h1>HEADING</h1><p>PARA<i>ITAL</i></p></body></html>")
        normalized = normalizer.normalize()
        self.assertEquals("titleheadingparaital", normalized)

class TestComparator(unittest.TestCase):

    def setUp(self):
        pass

    def test___init__perfect(self):
        from webcompare import Comparator
        comparator = Comparator("foo", "foo")
        self.assertEquals(comparator.compare(), comparator.match_perfect)

    def test___init__nothing(self):
        from webcompare import Comparator
        comparator = Comparator("foo", "bar")
        self.assertEquals(comparator.compare(), comparator.match_nothing)

if __name__ == '__main__':
    unittest.main()

