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

    def test_count_html_errors(self):
        self.assertEquals(len(self.walker.count_html_errors("")), 1)
        self.assertEquals(len(self.walker.count_html_errors("<html></html>")), 3)
        self.assertEquals(len(self.walker.count_html_errors("<html><head><title BROKEN><body><p>Missing P</html>")), 3)

        

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
        from webcompare import Result, ErrorResult, BadOriginResult, BadTargetResult, GoodResult
        self.Result          = Result
        self.ErrorResult     = ErrorResult
        self.BadOriginResult = BadOriginResult
        self.BadTargetResult = BadTargetResult
        self.GoodResult      = GoodResult

    def test___init__origin(self):
        r = self.Result("originurl", 666, origin_time=42.0)
        self.assertEquals(r.result_type, "Result")
        self.assertEquals(r.origin_url, "originurl")
        self.assertEquals(r.origin_code, 666)
        self.assertEquals(r.origin_time, 42.0)
        self.assertEquals(r.target_url, None)
        self.assertEquals(r.target_code, None)
        self.assertEquals(r.comparisons, {})
        self.assertTrue("comp={}" in r.__str__())

    def test___init__target(self):
        r = self.Result("originurl", 666, target_url="targeturl", target_code=777, target_time=42.0)
        self.assertEquals(r.target_url, "targeturl")
        self.assertEquals(r.target_code, 777)
        self.assertEquals(r.target_time, 42.0)
        self.assertEquals(r.comparisons, {})
        self.assertTrue("comp={}" in r.__str__())

    def test___init__html_errors(self):
        r = self.Result("originurl", 200, origin_html_errors=["bad"], target_html_errors=["ugly"])
        self.assertEquals(r.origin_html_errors, 1)
        self.assertEquals(r.target_html_errors, 1)


    def test___init__comparisons(self):
        r = self.Result("originurl", 666, target_url="targeturl", target_code=777, comparisons={'fee': 42, 'fi':666, 'foo':0xDeadBeef})
        self.assertEquals(r.comparisons, {'fee': 42, 'fi':666, 'foo':0xDeadBeef})

    def test_subclasses(self):
        r = self.ErrorResult("originurl", 666)
        self.assertEquals(r.result_type, "ErrorResult")
        r = self.BadOriginResult("origin", 666)
        self.assertEquals(r.result_type, "BadOriginResult")
        r = self.BadTargetResult("origin", 666)
        self.assertEquals(r.result_type, "BadTargetResult")
        r = self.GoodResult("origin", 666)
        self.assertEquals(r.result_type, "GoodResult")
        
            
class TestWalkerJsonResults(unittest.TestCase):
    def setup(self):
        pass

    def test_json_results(self):
        import json
        from webcompare import Walker     
        from webcompare import ErrorResult, BadOriginResult, BadTargetResult, GoodResult
        walker = Walker("origin", "target")
        walker.results.extend([ErrorResult("e1", 0),
                               BadOriginResult("bo1", 0), BadOriginResult("bo2", 0),
                               BadTargetResult("bt1", 0), BadTargetResult("bt2", 0),
                               GoodResult("g1", 0), GoodResult("g2", 0),
                               ])
        results = json.loads(walker.json_results())
        stats = results['results']['stats']
        self.assertEquals(stats['ErrorResult'], 1)
        self.assertEquals(stats['BadOriginResult'], 2)
        self.assertEquals(stats['BadTargetResult'], 2)
        self.assertEquals(stats['GoodResult'], 2)


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
        self.assertTrue("Feeling Lucky" in r.content)
        self.assertNotEqual(r.htmltree, None)
        
                        
class TestUrlManglers(unittest.TestCase):
    def SetUp(self):
        pass

    def test_normalize_url(self):
        from webcompare import Walker
        w = Walker("ignore", "ignore", ['\\?.*', '#.*', '/RSS.*', '<bound.*'])
        self.assertEquals(w._normalize_url("http://example.com?querystring"), "http://example.com")
        self.assertEquals(w._normalize_url("http://example.com#fragment"), "http://example.com")
        self.assertEquals(w._normalize_url("http://example.com/something"), "http://example.com/something")
        self.assertEquals(w._normalize_url("http://example.com/<bound method Application.absolute_url of <Application at >>"), "http://example.com/")
        self.assertEquals(w._normalize_url("http://example.com/something/RSS"), "http://example.com/something")
        
if __name__ == '__main__':
    unittest.main()

