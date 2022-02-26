import os
import typing
import json
import dataclasses
import dataclasses_json

@dataclasses_json.dataclass_json
@dataclasses.dataclass
class CacheItem:

    # description text derived from meta tags of document
    description: str

    # error while retrieving description
    description_error: str

    # error description - if selenium lookup is enabled.
    description_error_selenium: str

    # the language of the description (derived from language recognition model run over description text)
    language_description: str

    # http content language header (optional)
    http_content_language: str

    # language attribue in body tag of html response (optional)
    html_document_language: str

    translations: typing.Dict[str, str]

class DescriptionCacheBase:
    description_cache_file = 'description_cache.json'
    description_cache_file_with_translation = 'description_cache_with_translation.json'

    def __init__(self):
        self.map_url_to_descr = {}
        self.map_url_to_descr_changed = False

    @staticmethod
    def set_file_name(name):
        DescriptionCacheBase.description_cache_file = name

    def read_description_cache(self):
        if os.path.isfile(DescriptionCacheBase.description_cache_file):
            with open(DescriptionCacheBase.description_cache_file, 'r') as cache_file:
                self.map_url_to_descr = json.load(cache_file)

    def write_description_cache(self):
        if self.map_url_to_descr_changed:
            with open(DescriptionCacheBase.description_cache_file, 'w') as cache_file:
                json.dump( self.map_url_to_descr, cache_file, indent=2 )
            self.map_url_to_descr_changed = False
            return True
        return False

    def set_changed(self):
        self.map_url_to_descr_changed = True

    def cache_get(self, url):
        descr = self.map_url_to_descr.get(url, None)
        if descr is not None and descr != "":
            return CacheItem.from_dict(descr)
        return None

    def cache_set(self, url, obj):
        self.map_url_to_descr[ url ] = obj.to_dict()
        self.map_url_to_descr_changed = True
