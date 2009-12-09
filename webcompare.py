import logging
from urlparse import urlparse

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
        self.origin_urls_todo = []
        self.origin_urls_visited = []

    def _fetch_url(self, url):
        """Retrieve a page by URL, return as HTTP response (with response code, etc)
        This could be overriden, e.g., to use an asynchronous call.
        """
        pass
    
    def _get_target_url(self, origin_url):
        """Return URL for target based on origin_url.
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
        return self.origin_url_base.startswith(url)
    
    def add_comparator(self, comparator_function):
        """Add a comparator method to the list of compartors to try.
        Each compartor should return a floating point number between
        0.0 and 1.0 indicating how "close" the match is.
        """
        self.compartors.append(comparator_function)

        
    def walk_and_compare(self, origin_url=None):
        """Start at origin_url, generate target urls, run comparators, return dict of results.
        If there are no comparators, we will just return all the origin and target urls
        and any redirects we've encountered. 
        I need to think about how to do this,
        need to dork with the params.
        """
        if origin_url == None:
            origin_url = self.origin_url_base
        if origin_url in self.origin_urls_visited:
            logging.info("Already visited target_url=%s" % origin_url)
        elif not self._is_within_origin(origin_url):
            logging.warning("url=%s is not within origin_url=%s" % (origin_url, self.origin_url))
        else:
            self.origin_urls_visited.append(origin_url)
            target_url = self._get_target_url(origin_url)
            response = self._get_target_url(target_url)
            # ... parse good response for URLs, add to todo list
            
            
