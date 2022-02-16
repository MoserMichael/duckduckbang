import os
import json
import dataclasses
import dataclasses_json
import scrapscrap

@dataclasses_json.dataclass_json
@dataclasses.dataclass
class CacheItem:
    description: str

class DescriptionCache:
    description_cache_file = 'description_cache.json'
    ignore_set = {"www.accuweather.com", "www.adidas.fr", "aitopics.org", "www.appannie.com", "www.appannie.com", "www.albumartexchange.com"}

    def __init__(self, enable_http_client, enable_selenium):

        self.enable_selenium = enable_selenium
        self.enable_http_client = enable_http_client

        self.map_url_to_descr = {}
        self.map_url_to_descr_changed = False

        self.cache_load_ok = 0
        self.cache_load_failed = 0

    def show(self, prefix="", suffix=""):
        print(f"{prefix} Total: new lookups succeeded: {self.cache_load_ok} new lookups failed: {self.cache_load_failed} number of {suffix}")


    def read_description_cache(self):
        if os.path.isfile(DescriptionCache.description_cache_file):
            with open(DescriptionCache.description_cache_file, 'r') as cache_file:
                self.map_url_to_descr = json.load(cache_file)

    def write_description_cache(self):
        if self.map_url_to_descr_changed:
            with open(DescriptionCache.description_cache_file, 'w') as cache_file:
                json.dump( self.map_url_to_descr, cache_file, indent=2 )
            self.map_url_to_descr_changed = False

    def cache_lookup(self, url):
        print(f"cache_lookup {url}")
        descr = self.map_url_to_descr.get(url, None)
        if descr is not None and descr != "":
            return CacheItem.from_dict(descr), True

        if not self.enable_http_client:
            if url in DescriptionCache.ignore_set:
                return None, True

        descr, language, error_desc =  scrapscrap.gettitle.get_meta_descr(url, self.enable_http_client, self.enable_selenium)

        if scrapscrap.Global.trace_on:
            if error_desc is not None:
                print(f"Error: {error_desc}")
            else:
                print(f"url: {url}\ndescr: {descr}\nlanguage: {language}")

        is_in_map = url in self.map_url_to_descr

        # not sure if a scanning error should be put into the db, it could be a transient error...
#        if self.enable_selenium and error_desc is not None:
#             descr = error_desc,

        self.map_url_to_descr[url] = descr
        self.map_url_to_descr_changed = True
        self.write_description_cache()

        if descr is not None and descr != "" and error_desc is None:
            self.cache_load_ok += 1
        else:
            # don't count repeated failures.
            if not is_in_map:
                self.cache_load_failed += 1

        return CacheItem.from_dict(descr), False

    def cache_get(self, url):
        descr = self.map_url_to_descr.get(url, None)
        if descr is not None and descr != "":
            return CacheItem.from_dict(descr)
        return None
