#!/usr/bin/env python3
import argparse
import json
import os
from pprint import pprint
from datetime import datetime
import re
import gettitle
from comm import *

# sys.setdefaultencoding() does not exist, here!
#reload(sys)  # Reload does the trick!
#sys.setdefaultencoding('UTF8')

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
                json.dump( self.map_url_to_descr, cache_file )
            self.map_url_to_descr_changed = False

    def cache_lookup(self, url):
        print(f"cache_lookup {url}")
        descr = self.map_url_to_descr.get(url, None)
        if descr is not None and descr != "":
            return descr, True

        if url in DescriptionCache.ignore_set:
            return "", True

        descr =  gettitle.get_meta_descr(url, self.enable_http_client, self.enable_selenium)

        is_in_map = url in self.map_url_to_descr

        self.map_url_to_descr[url] = descr
        self.map_url_to_descr_changed = True
        self.write_description_cache()

        if descr is not None and descr != "":
            self.cache_load_ok += 1
        else:
            # don't count repeated failures.
            if not is_in_map:
                self.cache_load_failed += 1

        return descr, False

    def cache_get(self, url):
        descr = self.map_url_to_descr.get(url, None)
        if descr is not None and descr != "":
            return descr
        return None


class DuckStuff:
    #the host
    url = 'https://duckduckgo.com'

    def __init__(self, enable_http_client, enable_selenium):
        self.soup_builder = BSoup()
        self.desc_cache = DescriptionCache(enable_http_client, enable_selenium)
        self.desc_cache.read_description_cache()
        self.map_url_to_id = {}
        self.clean_tag = re.compile('<.*?>')

    def build_cache(self):
        json_data = self.soup_builder.get_json(DuckStuff.url + "/bang.js")
        failed_lookups = []

        cur_item = 0
        total_items = len(json_data)
        for entry in json_data:
            url = entry.get("d")

            before_lookup = datetime.now()
            description, cache_hit = self.desc_cache.cache_lookup( url) #, self.soup_builder )
            after_lookup = datetime.now()

            if description is None or description == "":
                failed_lookups.append( url )
            else:
                print(f"description: {description}")

            time_diff = after_lookup - before_lookup
            self.desc_cache.show(prefix="", suffix=f"cache_hit: {cache_hit} current: {cur_item+1}/{total_items} lookup_time: {repr(time_diff)}")
            cur_item += 1

        self.desc_cache.show("Total:")

        if len(failed_lookups) != 0:
            with open("failed_lookups.txt", "w") as log_file:
                print("failed lookups:\n", "\n".join(failed_lookups) )
                log_file.write("\n".join(failed_lookups))


    def get_all(self):
        json_data = self.soup_builder.get_json(DuckStuff.url + "/bang.js")

        all_bangs = {}
        set_of_bangs = {}
        num_entries = 0

        for entry in json_data:
            #print("Category {} SubCategory {}".format(entry.get("c"), entry.get("sc")))
            sub_cat = entry.get("sc")
            cat = entry.get("c")
            if not cat is None and not sub_cat is None:
                cat_obj = all_bangs.get(cat)
                if cat_obj is None:
                    all_bangs[cat] = {}
                    cat_obj = all_bangs.get(cat)

                sub_cat_obj = cat_obj.get(sub_cat)
                if sub_cat_obj is None:
                    cat_obj[sub_cat] = []
                    sub_cat_obj = cat_obj.get(sub_cat)

            url = entry.get("d")

            entry = (entry.get("t"), entry.get("s"), url)
            sub_cat_obj.append(entry)
            num_entries = num_entries + 1
            set_of_bangs[entry[0]] = 1

        if Global.trace_on:
            pprint(all_bangs)

        return all_bangs, num_entries, len(set_of_bangs.keys()), json_data

    def build_toolip_help_list(self, json_data, out_file):
        next_id = 0
        out_file.write("""
<script>
tool_tip_array=[
""")
        for entry in json_data:
            url = entry.get("d")
            id_value = self.map_url_to_id.get(url)
            if id_value is None:
                self.map_url_to_id[url] = next_id
                next_id += 1
                out_file.write(f"\"{self.get_title(url)}\",\n")

        out_file.write("""
        ];

function h(elem) {
    elem.title = "kukukuku";
    //if (elem.attr("title")) {
    //   elem.title = tool_tip_array[ elem.id ]
    //}
}
</script>
""")

    def get_title(self, url):
        desc = self.desc_cache.cache_get(url)
        if desc is None:
            return url

        if desc.find('"') != -1:
            #print(f"Warning: description for {url} contains a quotation mark, desc: {desc}")
            desc = desc.replace('"', "&quot;")

        desc = desc.replace('\n', "\\n")

        desc = re.sub(self.clean_tag, '', desc)

        if desc.find(url) != -1:
            return desc

        return url + " - " + desc

#    def get_categories(self):
#
#        ms = self.soup_builder.get_soup(DuckStuff.url + "/bang")
#
#        ret_cats = []
#
#        for tag in ms.findAll('script'):
#            src_path = tag.get('src')
#
#            if not src_path is None:
#                data = self.soup_builder.get_data(DuckStuff.url + src_path)
#                data_str = data.decode("utf-8")
#
#                if data_str.find("BangCategories={") != -1:
#                    rex = re.search(r"BangCategories={([^}]*)}", data_str)
#                    if not rex is None:
#                        cts = re.findall(r"[^:]*:\[[^\]]*\],?", rex.group(1))
#                        for onectg in cts:
#                            tg = re.search(r"[^:]*", onectg).group(0)
#                            entries = re.findall(r"\"[^\"]*\"", onectg)
#                            ret_cats.append((tg, entries))
#
#        return ret_cats
#

    def show_cats(self, output_file_name):

        all_bangs, num_entries, unique_bangs, json_data = self.get_all()

        #pprint(all_bangs)

        with open(output_file_name, "w") as out_file:

            out_file.write("""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>title</title>
    <link rel="stylesheet" href="template/github-markdown.css">
  </head>
  <script>

  function onBang(bangText) {
    //document.location = "https://duckduckgo.com/?q=!" + bangText;

    window.parent.postMessage( '{ "cmd": "set-bang", "bang": "' + bangText + '"}', '*')
  }
  </script>

<body class="markdown-body">
<a id="top"/>

""")

            self.build_toolip_help_list(json_data, out_file)
            out_file.write("<table><tr><th>Category</th><th>Sub categories</th></tr>\n")
            link_num = 1

            all_bangs_keys = list(all_bangs)
            all_bangs_keys.sort()

            for cat in all_bangs_keys:
                entry_links = ""

                is_first = True

                all_bangs_cat = list(all_bangs[cat])
                all_bangs_cat.sort()

                for catentry in all_bangs_cat:
                    if not is_first:
                        entry_links = entry_links + ","
                    entry_links = entry_links + "&nbsp;"
                    is_first = False
                    entry_links = entry_links +  f"<a href=\"#{link_num}\">{catentry}</a>"
                    link_num = link_num + 1
                out_file.write(f"<tr><td>{cat}</td><td>{entry_links}</td>\n")
            out_file.write("</table>\n")

            link_num = 1
            num_columns = 3

            for cat in all_bangs_keys:

                all_bangs_cat = list(all_bangs[cat])
                all_bangs_cat.sort()


                for catentry in all_bangs_cat:
                    out_file.write(f"<hr/><p/><a id=\"{link_num}\"/>\n")
                    link_num += 1

                    out_file.write(f"<h3>{cat} / {catentry}</h3><p></p>\n")

                    pos = 0
                    out_file.write("<table width=\"100%\"><tr>\n")

                    cat_content = sorted(all_bangs[cat][catentry], key=lambda entry : entry[1])

                    for bang in cat_content:
                        if pos % num_columns == 0:
                            out_file.write("</tr><tr>")
                        out_file.write("<td>")
                        out_file.write(f"<span align=\"left\"><a id=\"{self.map_url_to_id[bang[2]]}\" onHover=\"javascript:h(self)\" href=\"javascript:onBang('{bang[0]}')\">{bang[1]}</a></span> <span style=\"float: right\">!<a id=\"{self.map_url_to_id[bang[2]]}\" onHover=\"javascript:h(self)\" href=\"javascript:onBang('{bang[0]}')\">{bang[0]}</a></span> &nbsp;")
                        out_file.write("</td>")
                        pos = pos + 1

                    while True:
                        if pos % num_columns == 0:
                            break
                        out_file.write("<td></td>")
                        pos = pos + 1

                    out_file.write("</tr></table>")

            out_file.write("\n<table width='100%'><tr><td>Generated on {}; number of entries {} unique bangs! {}</td></tr></table>\n<p><p><p>***eof***\n".format(datetime.now(), num_entries, unique_bangs))


def _parse_cmd_line():
    usage = """
Build the html for the duckduckbang meta search tool.
"""

    parse = argparse.ArgumentParser(
        description=usage, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    group = parse.add_argument_group("build cache")

    group.add_argument(
        "--cache",
        "-c",
        default=False,
        action="store_true",
        dest="build_cache",
        help="build json cache of site descriptions (long process)"
    )

    group.add_argument(
        "--selenium",
        "-s",
        default=False,
        action="store_true",
        dest="selenium",
        help="enable selenium download"
    )

    group.add_argument(
        "--http-client",
        "-l",
        default=True,
        action="store_false",
        dest="http_client",
        help="disable default python http client http.client (default: enabled)"
    )

    group = parse.add_argument_group("build html pages")

    group.add_argument(
        "--html",
        "-t",
        default=False,
        action="store_true",
        dest="build_html",
        help="building of html files (default off)"
    )

    group.add_argument(
        "--verbose",
        "-v",
        default=False,
        action="store_true",
        dest="verbose",
        help="verbose debug output"
    )

    group.add_argument(
        "--debug",
        "-d",
        default=False,
        action="store_true",
        dest="debug",
        help="show content of downloaded page"
    )


    return parse.parse_args()

def _run_cmd():
    cmd = _parse_cmd_line()

    duck = DuckStuff(cmd.http_client, cmd.selenium)

    if cmd.build_cache:
        print("Building descriptions...")
        duck.build_cache()

    if cmd.build_html:
        print("Building html file...")
        duck.show_cats("all_cats.html")

if __name__ == '__main__':
    _run_cmd()

#for link in BeautifulSoup(data, parse_only=SoupStrainer('a')):
#    if link.has_attr('href'):
#        print(link['href'])
