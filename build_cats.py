#!/usr/bin/env python3
import json
import os
from pprint import pprint
from datetime import datetime
import gettitle
from comm import *

# sys.setdefaultencoding() does not exist, here!
#reload(sys)  # Reload does the trick!
#sys.setdefaultencoding('UTF8')

class DescriptionCache:
    description_cache_file = 'description_cache.json'
    ignore_set = {"www.accuweather.com", "www.adidas.fr", "aitopics.org", "www.appannie.com", "www.appannie.com"}

    def __init__(self):
        self.map_url_to_descr = {}
        self.map_url_to_descr_changed = False

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

        descr = self.map_url_to_descr.get(url, None)
        if descr is not None and descr != "":
            return descr
        if url not in DescriptionCache.ignore_set:
            descr =  gettitle.get_meta_descr(url)
            if descr is not None:
                self.map_url_to_descr[url] = descr
                self.map_url_to_descr_changed = True
                self.write_description_cache()
        else:
            descr = ""
        return descr


class DuckStuff:
    #the host
    url = 'https://duckduckgo.com'


    def __init__(self):
        self.soup_builder = BSoup()
        self.desc_cache = DescriptionCache()

    def get_all(self):
        json_data = self.soup_builder.get_json(DuckStuff.url + "/bang.js")


        all_bangs = {}
        set_of_bangs = {}
        num_entries = 0

        cache_lookup_ok = 0
        cache_lookup_failed = 0
        failed_lookups = []

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

            description = self.desc_cache.cache_lookup( url ) #, self.soup_builder )
            if description is None or description == "":
                print("failed lookup: {url}")
                cache_lookup_failed += 1
                failed_lookups.append( url )
            else:
                cache_lookup_ok += 1

            entry = (entry.get("t"), entry.get("s"), url, description)
            print(f"Cache lookup succeeded: {cache_lookup_ok} failed: {cache_lookup_failed}")
            if len(failed_lookups) != 0:
                with open("failed_lookups.txt", "w") as failed_lookups:
                    print("failed lookups:\n", "\n".join(failed_lookups) )
                    failed_lookups.write("\n".join(failed_lookups))

            sub_cat_obj.append(entry)
            num_entries = num_entries + 1
            set_of_bangs[entry[0]] = 1


        print(f"Total: Cache lookup succeeded: {cache_lookup_ok} failed: {cache_lookup_failed}")


        if Global.trace_on:
            pprint(all_bangs)

        return all_bangs, num_entries, len(set_of_bangs.keys())


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

        self.desc_cache.read_description_cache()

        all_bangs, num_entries, unique_bangs = self.get_all()

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
                        out_file.write("<span align=\"left\"><a title=\"{}\" href=\"javascript:onBang('{}')\">{}</a></span> <span style=\"float: right\">!<a title=\"{}\" href=\"javascript:onBang('{}')\">{}</a></span> &nbsp;".format(bang[2], bang[0], bang[1], bang[2], bang[0], bang[0]))
                        out_file.write("</td>")
                        pos = pos + 1

                    while True:
                        if pos % num_columns == 0:
                            break
                        out_file.write("<td></td>")
                        pos = pos + 1

                    out_file.write("</tr></table>")

            out_file.write("\n<table width='100%'><tr><td>Generated on {}; number of entries {} unique bangs! {}</td></tr></table>\n<p><p><p>***eof***\n".format(datetime.now(), num_entries, unique_bangs))



#---
#Global.trace_on = True
#Global.debug_on = True
DuckStuff().show_cats("all_cats.html")

#for link in BeautifulSoup(data, parse_only=SoupStrainer('a')):
#    if link.has_attr('href'):
#        print(link['href'])
