import http.client as client
from urllib.parse import urlparse
import urllib.request as request
import urllib
import http.cookiejar as cookiejar
#import mycookiejar as cookiejar
import ssl
import json
import gzip
import zlib
import brotli
import io
from pprint import pprint
import html5lib
#import cloudscraper

class Global:
    trace_on = False
    debug_on = False
    timeout_sec = None

class MyCookiePolicy(cookiejar.DefaultCookiePolicy):
    def set_ok(self, cookie, request):
        if Global.debug_on:
            print(f"MyCookiePolicy.set_ok cookie: {repr(cookie)} request: {repr(request)}")
        return True

    def return_ok(self, cookie, request):
        if Global.debug_on:
            print(f"MyCookiePolicy.return_ok cookie: {repr(cookie)} request: {repr(request)}")
        return True

    def domain_return_ok(self, domain, request):
        if Global.debug_on:
            print(f"MyCookiePolicy.domain_return_ok cookie: {repr(domain)} request: {repr(request)}")
        return True

    def path_return_ok(self, path, request):
        if Global.debug_on:
            print(f"MyCookiePolicy.path_return_ok cookie: {repr(path)} request: {repr(request)}")
        return True
#
# get soup over tls 1.2
#
class BSoup:

    user_agent =  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0"
    referer = 'https://google.com'
    accept_hdr = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    accept_lan = "en-US,en;q=0.5"
    accept_enc = "gzip, deflate, br"



    def __init__(self):
        self.map_host_to_conn = {}
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.cookiejar = cookiejar.CookieJar( policy = MyCookiePolicy() )

    def get_data(self, url):
        return self.get_data_imp(url, 1)

    @staticmethod
    def _get_charset(response: client.HTTPResponse) -> str:

        content = response.headers.get("Content-Type")

        if content is None:
            return "utf-8"

        try:
            info = content.split(';')[1]
            info = info.strip(' ')
            charset = info.split('=')[1]
        except IndexError:
            return "utf-8"
        else:
            return charset

        return "utf-8"

    def get_data_imp(self, url, depth):
        def get_hdr(hdrs, hdr_name):
            for name, value in hdrs.items():
                if name.lower() == hdr_name: #"location":
                    return value.strip()
            return None

        if Global.trace_on:
            print(f"url: {url} depth: {depth}")

        if depth > 20:
            raise ValueError(f"too many redirections {url}")

        parsed_url = urlparse(url, scheme='https', allow_fragments=True)
        if parsed_url.netloc == '':
            parsed_url = urlparse("//" + url, scheme='https', allow_fragments=True)

        host = parsed_url.netloc
        path = parsed_url.path

        #print(f"{url} {parsed_url} host: {type(host)} {host} path: {path}")

        if parsed_url.query:
            path += parsed_url.query

        conn = self.map_host_to_conn.get(host)

        if conn is None:
            if Global.timeout_sec is None:
                conn = client.HTTPSConnection(host, context=self.context)
            else:
                conn = client.HTTPSConnection(host, context=self.context, timeout=Global.timeout_sec)

            self.map_host_to_conn[host] = conn

        if Global.debug_on:
            conn.set_debuglevel(1)

        req = request.Request('https://'+url)
        self.cookiejar.add_cookie_header( req )

        # fake some user agent - put all header just like in firefox on osx.
        req_headers = {
          'User-Agent': BSoup.user_agent,
           #'referer': BSoup.referer,
          'Accept': BSoup.accept_hdr,
          'Accept-Language': BSoup.accept_lan,
          'Accept-Encoding':'gzip, deflate, br',
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
          'Sec-Fetch-Dest': 'document',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-Site': 'none',
          'Sec-Fetch-User': '?1'
        }

        if req.has_header("Cookie"):
            cookie_val =  req.get_header("Cookie")
            if Global.debug_on:
                print(f"SET_COOKIE: {cookie_val}")
            req_headers["Cookie"] = cookie_val

        if req.has_header("Cookie2"):
            cookie_val =  req.get_header("Cookie2")
            if Global.debug_on:
                print(f"SET_COOKIE2: {cookie_val}")
            req_headers["Cookie2"] = cookie_val

        conn.request("GET", path, headers=req_headers)

        resp = conn.getresponse()

        self.cookiejar.extract_cookies(resp, req)

        detected_charset = BSoup._get_charset(resp)
        
        # takes care of transfer encoding chunked. thanks!
        data = resp.read()

        headers = dict(resp.getheaders())

        content_encoding_hdr = get_hdr(headers,'content-encoding')
        if content_encoding_hdr is not None:
            if content_encoding_hdr.lower() == "gzip":
                data = gzip.decompress(data)
            elif content_encoding_hdr.lower() == "br":
                data = brotli.decompress(data)
            elif content_encoding_hdr.lower() == "deflate":
                data = zlib.decompress(data)
            else:
                print(f"Warning: unknown content encoding {content_encoding_hdr} for url: {url} !!!")


        content_language_hdr = get_hdr(headers, "content-language")

        if Global.trace_on:
            print(f"resp: {resp} status: {resp.status} charset: {detected_charset} headers: {dict(resp.getheaders())}")

        location_hdr = get_hdr(headers,'location')

        if location_hdr is not None:

            # some servers return encoded location header. brrr.
            #location_hdr = urllib.parse.unquote(location_hdr, encoding='utf-8', errors='replace')

            #print(f"redirect to: {headers['Location']}")
            if not location_hdr.startswith("/"):
                return self.get_data_imp(location_hdr, depth+1)
            else:
                return self.get_data_imp(url + location_hdr, depth+1)
        elif resp.status >= 300:
            raise ValueError(f"http error. response status {resp.status}")

        if Global.debug_on:
            print(f"host={host} path={path} data:\n{data}\n")

        return data, detected_charset, content_language_hdr


    def get_json(self, url):
        data, _, _ = self.get_data(url)

        json_rep = json.loads(data)

        if Global.trace_on:
            pprint(json_rep)

        return json_rep

#    def get_data_cloudfare(self, url):
#        scraper = cloudscraper.create_scraper()
#
#        url_with_schema = "https://" + url
#
#        print(f"url: {url_with_schema}")
#
#        text = scraper.get(url_with_schema).text
#        if Global.debug_on:
#            print(f"url: {url} data: {type(text)} {text}")
#        return text

    def get_soup(self, url):

        data, detected_charset, _ = self.get_data(url)
        data_file = io.StringIO(data.decode(detected_charset.lower()))

        return html5lib.parse(data_file, treebuilder="etree") #lxml")

#    def get_soup_cloudfare(self, url):
#        data = self.get_data_cloudfare(url)
#        data_file = io.StringIO(data)
#
#        return html5lib.parse(data_file, treebuilder="etree") #lxml")
#
