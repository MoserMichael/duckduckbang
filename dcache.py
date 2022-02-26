from dcachebase import CacheItem, DescriptionCacheBase
import scrapscrap

class DescriptionCache(DescriptionCacheBase):
    ignore_set = {"www.accuweather.com", "www.adidas.fr", "aitopics.org", "www.appannie.com", "www.appannie.com", "www.albumartexchange.com", "www.shaw.ca" }

    def __init__(self, enable_http_client, enable_selenium):
        super().__init__()
        self.enable_selenium = enable_selenium
        self.enable_http_client = enable_http_client

        self.cache_load_ok = 0
        self.cache_load_failed = 0

    def show(self, prefix="", suffix=""):
        print(f"{prefix} Total: new lookups succeeded: {self.cache_load_ok} new lookups failed: {self.cache_load_failed} number of {suffix}")

    def cache_lookup_load_if_missing(self, url):
        print(f"cache_lookup_load_if_missing {url}")

        rval = self.cache_get(url)
        if rval is not None:
            txt = rval.description
            if txt is not None and txt != "":
                print(f"cache entry with description already exists: {rval}")
                return rval, True


        if self.enable_http_client:
            if url in DescriptionCache.ignore_set:
                print(f"url in ignore set. url: {url}")
                return None, True

        print(f"fetching description. url: {url} enable_http: {self.enable_http_client} enable_selenium: {self.enable_selenium}")
        descr, html_document_language, http_content_language_hdr, error_desc =  scrapscrap.gettitle.get_meta_descr(url, self.enable_http_client, self.enable_selenium)

        if scrapscrap.Global.trace_on:
            if error_desc is not None:
                print(f"Error: {error_desc}")
            else:
                print(f"fetched description. url: {url}\ndescr: {descr}\nhtml-language: {html_document_language}\nhttp-content_language-hdr: {http_content_language_hdr}")

        is_in_map = url in self.map_url_to_descr

        # not sure if a scanning error should be put into the db, it could be a transient error...
        
        if self.enable_selenium and error_desc is not None and error_desc != "":
            error_desc_selenium = error_desc
            error_desc = ""
        else:
            error_desc_selenium = ""

        cache_item = CacheItem(descr, error_desc, error_desc_selenium, '', http_content_language_hdr, html_document_language, {})

        self.map_url_to_descr[url] = cache_item.to_dict()
        self.map_url_to_descr_changed = True
        self.write_description_cache()

        if descr is not None and descr != "" and error_desc is None:
            self.cache_load_ok += 1
        else:
            # don't count repeated failures.
            if not is_in_map:
                self.cache_load_failed += 1

        return cache_item, False


