import json


def convert():

    description_cache_file = 'description_cache.json'
    map_url_to_descr = {}

    with open(description_cache_file, 'r') as cache_file:
        map_url_to_descr = json.load(cache_file)

    for key, val in map_url_to_descr.items():
        val['translations'] = {}

    with open(description_cache_file, 'w') as cache_file:
        json.dump(map_url_to_descr, cache_file, indent=2 )

convert()
