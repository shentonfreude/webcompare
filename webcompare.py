import logging
from urlparse import urlparse
import urllib2
import lxml.html

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
        """Retrieve a page by URL, return as HTTP response (with response code, etc)
        This could be overriden, e.g., to use an asynchronous call.
        If this causes an exception, we just leave it for the caller.
        """
        return urllib2.urlopen(url)

    def _fetch_url_content(self, url):
        """Retrieve the content of a resource at a given URL.
        If this causes an exception, we just leave it for the caller.
        TODO: this should return a yield so we can handle large pages.
        """
        page = self._fetch_url(url)
        return page.read()
    
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
    
    def _get_urls(self, html, base_href):
        """Return list of objects representing absolute URLs found in the html.
        [(element, attr, link, pos) ...]
        TODO: May want to normalize these
        - Need to make URLs absolute, take into account this doc's URL as base (?)
        - .resolve_base_href()
        - .make_links_absolute(base_href, resolve_base_href=True)
        """
        tree = lxml.html.fromstring(html)
        tree.make_links_absolute(base_href, resolve_base_href=True)
        return tree.iterlinks()

    def add_comparator(self, comparator_function):
        """Add a comparator method to the list of compartors to try.
        Each compartor should return a floating point number between
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
            else:
                self.origin_urls_visited.append(origin_url)
                target_url = self._get_target_url(origin_url)
                self.origin_urls_visited.append(target_url)
                try:
                    response = None # don't leave any leftover stuff to confuse us
                    response = self._fetch_url(target_url)
                    code = response.code
                except urllib2.URLError, e:
                    logging.warning("Could not fetch target_url=%s -- %s" % (target_url, e))
                    code = e.code
                    # TODO: record and bail here, so we don't have to check code below.
                if code != 200:
                    logging.warning("No success code=%s finding target_url=%s" % (code, target_url))
                    # TODO: add code, (redirected) url to results dictlist
                else:
                    ct = response.headers['content-type'].split(';')[0]
                    if ct != "text/html":
                        logging.debug("Not parsing non-html content-type=%s" % ct)
                    else:
                        content = response.read()
                        # TODO: how do we get the real abs url or our response's request obj?
                        url_objs = self._get_urls(content, response.url)
                        for url_obj in url_objs:
                            url = url_obj[2]
                            if not self._is_within_origin(url):
                                logging.debug("Skip url=%s not within origin_url=%s" % (url, self.origin_url_base))
                            else:
                                logging.debug("adding URL=%s" % url_obj[2])
                                self.origin_urls_todo.append(url_obj[2])

            
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print "this is webcompare.py"
