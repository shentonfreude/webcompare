#!/usr/bin/env python

import logging
from urlparse import urlparse
import urllib2
import httplib
import lxml.html
from difflib import SequenceMatcher
from optparse import OptionParser
import json
import sys
from pprint import pprint as pp

class Result(object):
    """Return origin and target URL, HTTP success code, redirect urls, and dict/list of comparator operations.
    """
    def __init__(self, origin_url, origin_response_code,
                 target_url=None, target_response_code=None,
                 comparisons={}):
        self.origin_url = origin_url
        self.origin_response_code = origin_response_code
        self.target_url = target_url
        self.target_response_code = target_response_code
        self.comparisons = comparisons

    def __repr__(self):
        return dict(origin_url=self.origin_url, origin_response_code=self.origin_response_code,
                    target_url=self.target_url, target_response_code=self.target_response_code,
                    comparisons=self.comparisons)

    def __str__(self):
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
        try:
            self.content_length = int(self.http_response.headers['content-length'])
        except KeyError, e:
            self.content_length = len(self.content)
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
        """Return URL for target based on (absolute) origin_url.
        TODO: do I want to handle relative origin_urls?
        """
        if not origin_url.startswith(self.origin_url_base):
            raise ValueError, "origin_url=%s does not start with origin_url_base=%s" % (
                origin_url, self.origin_url_base)
        return origin_url.replace(self.origin_url_base, self.target_url_base, 1)

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

        
    def jsonify(self, r):
        """Return the JSON representation of a single result.
        """
        return dict(origin_url=r.origin_url, origin_response_code=r.origin_response_code,
                    target_url=r.target_url, target_response_code=r.target_response_code,
                    comparisons=r.comparisons)
    
    def json_results(self):
        """Return the JSON representation.
        Hopefully will allow clever JS tricks to render and sort in browser.
        """
        d = [self.jsonify(r) for r in self.results]
        return json.dumps(d, sort_keys=True, indent=4)
    
    def walk_and_compare(self):
        """Start at origin_url, generate target urls, run comparators, return dict of results.
        If there are no comparators, we will just return all the origin and target urls
        and any redirects we've encountered. 
        TODO: remove unneeded testing and logging, clean up if/else/continue
        """
        while self.origin_urls_todo:
            origin_url = self.origin_urls_todo.pop(0)
            logging.info("visited=%s todo=%s try url=%s" % (
                    len(self.origin_urls_visited),
                    len(self.origin_urls_todo),
                    origin_url))
            if origin_url in self.origin_urls_visited:
                logging.debug("Skip already visited target_url=%s" % origin_url)
                continue
            else:
                self.origin_urls_visited.append(origin_url)
                try:
                    origin_response = self._fetch_url(origin_url)
                except (urllib2.URLError, httplib.BadStatusLine), e:
                    logging.warning("Could not fetch origin_url=%s -- %s" % (origin_url, e))
                    result = Result(origin_url, getattr(e, 'code', 0)) # no HTTP code if DNS not found
                    self.results.append(result)
                    logging.info("result(err resp): %s" % result)
                    continue
                if origin_response.code != 200: # TODO: do I need this check?
                    logging.warning("No success code=%s finding origin_url=%s" % (
                            origin_response.code, origin_url))
                    result = Result(origin_url, origin_response.code)
                    self.results.append(result)
                    logging.info("result(err code): %s" % result)
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
                        result = Result(origin_url, origin_response.code,
                                        target_url=target_url, target_response_code=e.code)
                        self.results.append(result)
                        logging.info("result(err targ): %s" % result)
                        continue
                    comparisons = {}
                    if origin_response.htmltree == None or target_response.htmltree == None:
                        logging.warning("compare: None for origin htmltree=%s or target htmltree=%s" % (
                                origin_response.htmltree, target_response.htmltree))
                    else:
                        for comparator in self.comparators:
                            proximity = comparator.compare(origin_response, target_response)
                            comparisons[comparator.__class__.__name__] = proximity
                    result = Result(origin_url, origin_response.code,
                                    target_url=target_url, target_response_code=target_response.code,
                                    comparisons=comparisons)
                    self.results.append(result)
                    logging.info("result(OK  targ): %s" % result)

                    

# TODO: instantiation and invocation of Normalizer and Comparator feels stilted and awkward. 
            
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

    def unfraction(self, number):
        """Convert a 0 - 1 fractional into our match range"""
        return int((self.match_perfect - self.match_nothing) * number)
    
    def fuzziness(self, origin_text, target_text):
        """Return a fuzzy comparison value for the two (preprocessed) texts"""
        if origin_text and target_text:
            sm = SequenceMatcher(None,
                                 self.collapse_whitespace(origin_text).lower(),
                                 self.collapse_whitespace(target_text).lower())
            return self.unfraction(sm.ratio())
        else:
            return self.match_nothing
        
    def collapse_whitespace(self, text):
        """Collapse multiple whitespace chars to a single space.
        """
        return ' '.join(text.split())
        
    def compare(self, origin_response, target_response):
        """This is expected to be subclassed and then superclass invoked.
        """
        raise RuntimeError, "You need to subclass class=%s" % self.__class__.__name__
        
class TitleComparator(Comparator):
    """Compare <title> content from the reponse in a fuzzy way.
    Origin: "NASA Science", Target: "Site Map - NASA Science"
    """
    def compare(self, origin_response, target_response):
        origin_title = target_title = None
        try:
            origin_title = origin_response.htmltree.xpath("//html/head/title")[0].text
            target_title = target_response.htmltree.xpath("//html/head/title")[0].text
        except IndexError, e:
            logging.warning("Couldn't find a origin_title=%s or target_title=%s" % (origin_title, target_title))
            return self.match_nothing
        return self.fuzziness(origin_title, target_title)

class ContentComparator(Comparator):
    def compare(self, origin_response, target_response):
        return self.fuzziness(origin_response.content, target_response.content)

class BodyComparator(Comparator):
    def compare(self, origin_response, target_response):
        origin_body = target_body = None
        try:
            origin_body = origin_response.htmltree.xpath("//html/body")[0].text_content().lower()
            target_body = target_response.htmltree.xpath("//html/body")[0].text_content().lower()
        except (IndexError, AttributeError), e:
            logging.warning("Couldn't find a origin_body=%s or target_body=%s" % (origin_body, target_body))
            return self.match_nothing
        return self.fuzziness(origin_body, target_body)

class LengthComparator(Comparator):
    def compare(self, origin_response, target_response):
        olen = origin_response.content_length
        tlen = target_response.content_length
        if olen == 0 or tlen == 0:
            logging.warning("Zero length olen=%s tlen=%s" % (olen, tlen))
            return self.match_nothing
        olen = float(olen)
        tlen = float(tlen)
        if olen < tlen:
            fraction = olen / tlen
        else:
            fraction = tlen / olen
        return self.unfraction(fraction)
        
    
if __name__ == "__main__":
    usage = "usage: %prog [--verbose --file json_output_file_path] origin_url target_url"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="log info about processing")
    parser.add_option("-f", "--file", dest="filename", help="path to store the json results to (default is stdout)")
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Must specify origin and target urls")
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    w = Walker(args[0], args[1])
    w.add_comparator(LengthComparator())
    w.add_comparator(TitleComparator())
    w.add_comparator(BodyComparator())
    w.add_comparator(ContentComparator())
    w.walk_and_compare()
    if options.filename:
        f = open(options.filename, "w")
        ftmp = open(options.filename + ".tmp", "w")
    else:
        f = sys.stdout
        ftmp = open("/dev/null", "w") # likely to fail on WinDoze (but what doesn't?)
    f.write(w.json_results())
    f.close()
