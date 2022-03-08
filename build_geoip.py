#!/usr/bin/env python3

import socket
from geolite2 import geolite2
import dcachebase

class GetIPInfo:
    def __init__(self):
        self.reader = geolite2.reader()


    def resolve(self, name):
        try:
            ip_addr = socket.gethostbyname(name)
            match_entry = self.reader.get(ip_addr)
            if match_entry:
                country_info = match_entry.get('country')
                if country_info:
                    iso_code = country_info.get('iso_code')
                    if iso_code:
                        return iso_code.lower()

            print(f"Failed to get info for {name}")
        except Exception as exc:
            print(f"Error while determining country for {name} error: {exc}")
        return None


def run_get_geoip():
    cache = dcachebase.DescriptionCacheBase()

    cache.read_description_cache()
    num_set = 0

    info = GetIPInfo()

    for base_url, _ in cache.map_url_to_descr.items():
        entry_obj = cache.cache_get(base_url)
        if entry_obj:
            country = info.resolve(base_url)
            if country:
                print(f"host: {base_url} country: {country}")
                entry_obj.geoip_lan = country
                cache.cache_set(base_url, entry_obj)

    if cache.write_description_cache():
        print(f"*** description cache changed, number of items set: {num_set}")

run_get_geoip()
