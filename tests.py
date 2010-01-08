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

    def test_fetch_url_content(self):
        response = self.walker._fetch_url("http://google.com")
        self.assert_("Feeling Lucky" in response.content)
        
    def test__get_target_url_abs(self):
        turl = self.walker._get_target_url("http://origin.int/foo/bar/stuff.png")
        self.assertEquals(turl, "http://target.int/foo/bar/stuff.png")

    def test__get_target_url_fragment(self):
        turl = self.walker._get_target_url("http://origin.int/centers/hq/home/#maincontent")
        self.assertEquals(turl, "http://target.int/centers/hq/home/#maincontent")
        turl = self.walker._get_target_url("http://origin.int/centers/hq/home/index.html#maincontent")
        self.assertEquals(turl, "http://target.int/centers/hq/home/index.html#maincontent")


    def test__get_target_url_rel(self):
        self.assertRaises(ValueError, self.walker._get_target_url, "/foo/bar/stuff.png")

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
        from webcompare import Comparator
        self.comparator = Comparator()

    def test___init__perfect(self):
        self.assertRaises(RuntimeError, self.comparator.compare, "orig", "targ")

    def test_collapse_whitespace(self):
        self.assertEquals(self.comparator.collapse_whitespace("  foo   bar  "), "foo bar")
        
    def test_fuzziness(self):
        self.assertEquals(self.comparator.fuzziness("foo", "foo"), 100)
        self.assertEquals(self.comparator.fuzziness("foo", "foo "), 100)
        self.assertEquals(self.comparator.fuzziness("foo", "Foo"), 100)
        self.assertEquals(self.comparator.fuzziness("foo", "fool"), 85)
        
    def test_unfraction(self):
        self.assertEquals(self.comparator.unfraction(1.0), 100)
        self.assertEquals(self.comparator.unfraction(1), 100)
        self.assertEquals(self.comparator.unfraction(0.0), 0)
        self.assertEquals(self.comparator.unfraction(0), 0)
        self.assertEquals(self.comparator.unfraction(1.0/3.0), 33)

        
class TestResult(unittest.TestCase):

    def setUp(self):
        from webcompare import Result
        self.Result = Result

    def test___init__origin(self):
        r = self.Result("originurl", 666)
        self.assertEquals(r.origin_url, "originurl")
        self.assertEquals(r.origin_response_code, 666)
        self.assertEquals(r.target_url, None)
        self.assertEquals(r.target_response_code, None)
        self.assertEquals(r.comparisons, {})
        # this will prolly fail since dicts are unordered, but I'm not convinced __repr__ is the way to output this anyway so don't change yet
        self.assertEquals(r.__repr__(), {'comparisons': {}, 'origin_url': 'originurl', 'target_url': None, 'origin_response_code': 666, 'target_response_code': None})

    def test___init__target(self):
        r = self.Result("originurl", 666, "targeturl", 777)
        self.assertEquals(r.origin_url, "originurl")
        self.assertEquals(r.origin_response_code, 666)
        self.assertEquals(r.target_url, "targeturl")
        self.assertEquals(r.target_response_code, 777)
        self.assertEquals(r.comparisons, {})
        self.assertEquals(r.__repr__(), {'comparisons': {}, 'origin_url': 'originurl', 'target_url': 'targeturl', 'origin_response_code': 666, 'target_response_code': 777})

    def test___init__comparisons(self):
        r = self.Result("originurl", 666, "targeturl", 777, [1,2,3])
        self.assertEquals(r.comparisons, [1,2,3])

class TestResponse(unittest.TestCase):
    def setUp(self):
        from webcompare import Response
        from urllib2 import urlopen
        self.Response = Response
        self.urlopen = urlopen
        self.url = "http://google.com"
        
    def test_http_response(self):
        r = self.Response(self.urlopen(self.url))
        self.assertEquals(r.code, 200)
        self.assertEquals(r.url, "http://www.google.com/")
        self.assertEquals(r.content_type, "text/html; charset=ISO-8859-1")
        self.assertTrue("I'm Feeling Lucky" in r.content)
        self.assertNotEqual(r.htmltree, None)
        
                        
class TestUrlManglers(unittest.TestCase):
    def SetUp(self):
        pass
    def test_normalize_url(self):
        from webcompare import Walker
        w = Walker("ignore", "ignore")
        self.assertEquals(w._normalize_url("http://example.com?querystring"), "http://example.com")
        self.assertEquals(w._normalize_url("http://example.com#fragment"), "http://example.com")
        self.assertEquals(w._normalize_url("http://example.com/something"), "http://example.com/something")
        self.assertEquals(w._normalize_url("http://example.com/<bound method Application.absolute_url of <Application at >>"), "http://example.com/")
        self.assertEquals(w._normalize_url("http://example.com/something/RSS"), "http://example.com/something")
        
if __name__ == '__main__':
    unittest.main()

