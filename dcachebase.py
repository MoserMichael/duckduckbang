import os
import typing
import json
import dataclasses
import dataclasses_json
import globs

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

    # auto translation of descriptions
    translations: typing.Dict[str, str]

    # geo ip language (determined from host)
    geoip_lan: str

class FlagList:
    def __init__(self):
        self.flag_list = {}

    def read(self):
        if not os.path.isfile(globs.Globals.description_cache_file):
            raise ValueError(f"file not found {globs.Globals.description_cache_file}")

        with open(globs.Globals.flag_list, 'r') as flags_file:
            lines = flags_file.readlines()
            for line in lines:
                if line != "":
                    pos = line.find(".")
                    self.flag_list[ line[:pos] ] = 1

        print(f"countries: {' '.join(list(self.flag_list.keys()))}")

    def has_flag(self, country_code):
        return self.flag_list.get(country_code) is not None

class DescriptionCacheBase:

    def __init__(self):
        self.map_url_to_descr = {}
        self.map_url_to_descr_changed = False

        self.flag_list = FlagList()
        self.flag_list.read()

    @staticmethod
    def set_file_name(name):
        globs.Globals.description_cache_file = name

    def read_description_cache(self):
        if os.path.isfile(globs.Globals.description_cache_file):
            with open(globs.Globals.description_cache_file, 'r') as cache_file:
                self.map_url_to_descr = json.load(cache_file)

    def write_description_cache(self):
        if self.map_url_to_descr_changed:
            with open(globs.Globals.description_cache_file, 'w') as cache_file:
                json.dump( self.map_url_to_descr, cache_file, indent=2 )
            self.map_url_to_descr_changed = False
            return True
        return False

    def set_changed(self):
        self.map_url_to_descr_changed = True

    def cache_get(self, url):
        descr = self.map_url_to_descr.get(url, None)
        if descr is not None:
            return CacheItem.from_dict(descr)
        return None

    def cache_set(self, url, obj):
        self.map_url_to_descr[ url ] = obj.to_dict()
        self.map_url_to_descr_changed = True


    def get_country(self, cache_item):

        # try html document language first (know it's misleading, but very few sites are setting the http-content-language header correctly...)
        lan = cache_item.html_document_language
        country = ""
        pos = lan.find("-")
        if pos == -1:
            pos = lan.find("_")
        if pos != -1:
            country = lan[pos+1:]
            print(f"lan- {country}")
            if self.flag_list.has_flag(country):
                return country
            country = lan[:pos]
            print(f"-lan {country}")
        else:
            country = lan
            print(f"lan {country}")

        if country == "":
            if cache_item.language_description.startswith("__label__"):
                country = cache_item.language_description[ len("__label__") : ]
                print(f"::lan {country}")

        if country != "":
            if self.flag_list.has_flag(country):
                return country

        # use country from geopid as last resort.
        country = cache_item.geoip_lan

        if self.flag_list.has_flag(country):
            return country

        print(f"no such country: {country} {repr(cache_item)}")
        return ""
