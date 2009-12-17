import logging
from urlparse import urlparse
import urllib2
import lxml.html

# TODO:
# - lxml.html.clean: can it strip all HTML markup?

class Result(object):
    """Return origin and target URL, HTTP success code, redirect urls, and dict/list of comparator operations.
    """
    def __init__(self, origin_url, origin_response_code,
                 target_url=None, target_response_code=None,
                 comparisons=[]):
        self.origin_url = origin_url
        self.origin_response_code = origin_response_code
        self.target_url = target_url
        self.target_response_code = target_response_code
        self.comparisons = comparisons

    def __repr__(self):
        return "<Result o=%s oc=%s t=%s tc=%s comp=%s>" % (
            self.origin_url, self.origin_response_code,
            self.target_url, self.target_response_code,
            self.comparisons)


class Response(object):
    """Capture HTTP response and content, as a lxml tree if HTML.
    Store info returned from, e.g., urllib2.urlopen(url)
    We need to read content once since we can't reread already-read content.
    We could parse this and save contained URLs? Not generic enough?
    TODO: should subclass (undocumented) urllib2.urlopen() return object urllib.addinfourl ?
          instead of copying all its attrs into our own? 
    TODO: should we avid non-html content?
    """
    def __init__(self, http_response):
        self.http_response = http_response
        self.code = self.http_response.code
        self.url = self.http_response.geturl()
        self.content_type = self.http_response.headers['content-type']
        self.content = self.http_response.read()
        if self.content_type.startswith("text/html"):
            self.htmltree = lxml.html.fromstring(self.content)
            self.htmltree.make_links_absolute(self.url, resolve_base_href=True)
        else:
            self.htmltree = None
        
class Walker(object):
    """
    Walk origin URL, generate target URLs, retrieve both pages for comparison.
    """

    def __init__(self, origin_url_base, target_url_base):
        """Specify origin_url and target_url to compare.
        e.g.: w = Walker("http://oldsite.com", "http://newsite.com")
        TODO:
        - Limit to subtree of origin  like http://oldsite.com/forums/
        """
        self.origin_url_base = origin_url_base
        self.target_url_base = target_url_base
        self.target_url_parts = urlparse(target_url_base)
        self.comparators = []
        self.results = []
        self.origin_urls_todo = [self.origin_url_base]
        self.origin_urls_visited = []

    def _texas_ranger(self):
        return "I think our next place to search is where military and wannabe military types hang out."

    def _fetch_url(self, url):
        """Retrieve a page by URL, return as Response object (code, content, htmltree, etc)
        This could be overriden, e.g., to use an asynchronous call.
        If this causes an exception, we just leave it for the caller.
        """
        return Response(urllib2.urlopen(url))
    
    def _get_target_url(self, origin_url):
        """Return URL for target based on origin_url.
        TODO: ? use lxml.html.rewrite_links(repl_func, ...)
        """
        u = urlparse(origin_url)
        return "%s://%s%s%s%s%s" % (self.target_url_parts.scheme,
                                    self.target_url_parts.netloc,
                                    u.path,
                                    u.params,
                                    u.query,
                                    u.fragment,
                                    )

    def _is_within_origin(self, url):
        """Return whether a url is within the origin_url hierarchy.
        Not by testing the URL or anything clever, but just comparing
        the first part of the URL.
        """
        return url.startswith(self.origin_url_base)
    
    def _get_urls(self, html, base_href): # UNUSED?
        """Return list of objects representing absolute URLs found in the html.
        [(element, attr, link, pos) ...]
        TODO: May want to normalize these
        - Need to make URLs absolute, take into account this doc's URL as base (?)
        - .resolve_base_href()
        - .make_links_absolute(base_href, resolve_base_href=True)
        - See absolutizing here:
          http://blog.ianbicking.org/2008/12/10/lxml-an-underappreciated-web-scraping-library
        """
        tree = lxml.html.fromstring(html)
        tree.make_links_absolute(base_href, resolve_base_href=True)
        return tree.iterlinks()

    def add_comparator(self, comparator_function):
        """Add a comparator method to the list of comparators to try.
        Each comparator should return a floating point number between
        0.0 and 1.0 indicating how "close" the match is.
        """
        self.comparators.append(comparator_function)

        
    def walk_and_compare(self):
        """Start at origin_url, generate target urls, run comparators, return dict of results.
        If there are no comparators, we will just return all the origin and target urls
        and any redirects we've encountered. 
        """
        while self.origin_urls_todo:
            origin_url = self.origin_urls_todo.pop(0)
            logging.info("todo=%s visited=%s try url=%s" % (
                    len(self.origin_urls_todo),
                    len(self.origin_urls_visited),
                    origin_url))
            if origin_url in self.origin_urls_visited:
                logging.debug("Skip already visited target_url=%s" % origin_url)
                continue
            else:
                self.origin_urls_visited.append(origin_url)
                try:
                    origin_response = self._fetch_url(origin_url)
                except urllib2.URLError, e:
                    logging.warning("Could not fetch origin_url=%s -- %s" % (origin_url, e))
                    self.results.append(Result(origin_url, e.code))
                    continue
                if origin_response.code != 200: # TODO: do I need this check?
                    logging.warning("No success code=%s finding origin_url=%s" % (
                            origin_response.code, origin_url))
                    self.results.append(Result(origin_url, origin_response.code))
                    continue
                else:
                    if origin_response.content_type.startswith("text/html"):
                        for url_obj in origin_response.htmltree.iterlinks():
                            url = url_obj[2]
                            if not self._is_within_origin(url):
                                logging.debug("Skip url=%s not within origin_url=%s" % (url, self.origin_url_base))
                            elif url not in self.origin_urls_todo:
                                logging.debug("adding URL=%s" % url)
                                self.origin_urls_todo.append(url)
                    target_url = self._get_target_url(origin_url)
                    logging.debug("about to fetch target_url=%s" % target_url)
                    try:
                        target_response = self._fetch_url(target_url)
                    except urllib2.URLError, e:
                        logging.warning("Could not fetch target_url=%s -- %s" % (target_url, e))
                        self.results.append(Result(origin_url, origin_response.code,
                                                   target_url=target_url, target_response_code=e.code))
                        continue
                    # If we got here, we got origin and target so run compare HTML trees
                    # TODO BUGBUG: does the first comparator's read() consume all data
                    # which would cause the second to get nothing? If so, what do we do? 
                    comparisons = []
                    for comparator in self.comparators:
                        proximity = comparator.compare(origin_response.htmltree, target_response.htmltree)
                        logging.info("comparator=%s proxmity=%s" % (comparator,proximity))
                        comparisons.append(proximity)
                    self.results.append(Result(origin_url, origin_response.code,
                                               target_url=target_url, target_response_code=target_response.code,
                                               comparisons=comparisons))

                    


# TODO: instantiation and invocation of Normalizer and Comparator
#       feels stilted and awkward. 
            
class Normalizer(object):
    """TODO: should I be subclassing an LXML stipper? (oh baby)
    """
    def __init__(self, htmlstring):
        self.htree = lxml.html.fromstring(htmlstring)
    def normalize(self):
        return self.htree.text_content().lower() # TODO removes spaces implied by tags??

class Comparator(object):
    """Compare HTML trees, return number 0-100 representing less-more similarity.
    Examples:
    - compare normalized <title>
    - compare length of normalized text
    - compare (fuzzily) similarity of normalized
    - compare (fuzzily) rendered web page image
    - compare 'features' extracted with OpenCalais et al
    TODO: are we going to compare non-HTML responses?
          If so, we can't presume HTML-Tree objects as inputs.
    """
    def __init__(self):
        self.match_nothing = 0
        self.match_perfect = 100

    def compare(self, origin_response, target_response):
        """This is expected to be subclassed and then superclass invoked.
        """
        if origin_htmltree == None and target_htmltree == None:
            return self.match_perfect
        if origin_htmltree == None or target_htmltree == None:
            logging.warning("compare: None for origin_htmltree=%s or target_htmltree=%s" % (
                    origin_htmltree, target_htmltree))
            return self.match_nothing
        
class ContentComparator(Comparator):
    """Compare content from the reponse
    """
    def compare(self, origin_htmltree, target_htmltree):
        #TODO: something like: self.super(compare(original_html, target_html))
        if origin_htmltree == None and target_htmltree == None:
            return self.match_perfect
        if origin_htmltree == None or target_htmltree == None:
            logging.warning("compare: None for origin_htmltree=%s or target_htmltree=%s" % (
                    origin_htmltree, target_htmltree))
            return self.match_nothing
        if origin_htmltree.text_content() == target_htmltree.text_content():
            return self.match_perfect
        else:
            return self.match_nothing
        
class TitleComparator(Comparator):
    """Compare <title> content from the reponse
    """
    # TODO BUGBUG: this seems to get '' from read() even if only comparator, why??
    def compare(self, origin_htmltree, target_htmltree):
        #import pdb; pdb.set_trace()
        if origin_htmltree == None and target_htmltree == None:
            return self.match_perfect
        if origin_htmltree == None or target_htmltree == None:
            logging.warning("compare: None for origin_htmltree=%s or target_htmltree=%s" % (
                    origin_htmltree, target_htmltree))
            return self.match_nothing
        try:
            origin_title = origin_htmltree.xpath("//html/head/title")[0].text
            target_title = target_htmltree.xpath("//html/head/title")[0].text
        except Exception, e:
            print "HELP ME WHAT IS MY EXCEPTION e=%s" % e
            return self.match_nothing
        if origin_title == target_title:
            return self.match_perfect
        else:
            return self.match_nothing

class BodyComparator(Comparator):
    def compare(self, origin_htmltree, target_htmltree):
        if origin_htmltree == None and target_htmltree == None:
            return self.match_perfect
        if origin_htmltree == None or target_htmltree == None:
            logging.warning("compare: None for origin_htmltree=%s or target_htmltree=%s" % (
                    origin_htmltree, target_htmltree))
            return self.match_nothing
        try:
            origin_body = origin_htmltree.xpath("//html/body")[0].text_content.lower()
            target_body = origin_htmltree.xpath("//html/body")[0].text_content.lower()
        except Exception, e:
            print "HELP ME WHAT IS MY EXCEPTION e=%s" % e
            return self.match_nothing
        if origin_body == target_body:
            return self.match_perfect
        else:
            return self.match_nothing
            
        
def testit():
    from pprint import pprint as pp
    w = Walker("http://www.nasa.gov/centers/hq/home/", "http://www.nasa.gov/centers/hq/home/")
    #"http://chris.shenton.org/recipes/bread", "http://chris.shenton.org/recipes/bread")
    w.add_comparator(ContentComparator())
    w.add_comparator(TitleComparator())
    w.add_comparator(BodyComparator())
    w.walk_and_compare()
    pp(w.results)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print "this is webcompare.py"
