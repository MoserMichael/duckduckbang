#!/usr/bin/env python3
import argparse
from pprint import pprint
from datetime import datetime
import re
from dcache import DescriptionCache
import scrapscrap
import globs

# sys.setdefaultencoding() does not exist, here!
#reload(sys)  # Reload does the trick!
#sys.setdefaultencoding('UTF8')


class DuckStuff:

    MODE_SHOW_ALL_LANGUAGES=1
    MODE_SHOW_TRANSLATION=2

    #the host
    url = 'https://duckduckgo.com'

    def __init__(self, enable_http_client, enable_selenium, mode):
        self.soup_builder = scrapscrap.BSoup()
        self.desc_cache = DescriptionCache(enable_http_client, enable_selenium)
        self.desc_cache.read_description_cache()
        self.clean_tag = re.compile('<.*?>')
        self.enable_http_client = enable_http_client
        self.map_url_to_id = {}
        self.out_file = None
        self.mode = mode
        self.text_set = {}
        self.check_for_regx = None

    def build_cache(self):
        json_data = self.soup_builder.get_json(DuckStuff.url + "/bang.js")
        failed_lookups = []

        cur_item = 0
        total_items = len(json_data)
        for entry in json_data:
            url = entry.get("d")

            before_lookup = datetime.now()
            description, cache_hit = self.desc_cache.cache_lookup_load_if_missing(url) #, self.soup_builder )
            after_lookup = datetime.now()

            if description is None or description.description == "":
                failed_lookups.append( url )
            else:
                print(f"description: {repr(description)}")


            time_diff = after_lookup - before_lookup
            self.desc_cache.show(prefix="", suffix=f"cache_hit: {cache_hit} current: {cur_item+1}/{total_items} lookup_time: {repr(time_diff)}")
            cur_item += 1

        self.desc_cache.show("Total:")

        if len(failed_lookups) != 0:
            with open(globs.Globals.failed_lookups, "w") as log_file:
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

        if scrapscrap.Global.trace_on:
            pprint(all_bangs)

        return all_bangs, num_entries, len(set_of_bangs.keys()), json_data

    @staticmethod
    def write_hdr_pc(out_file):
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

    @staticmethod
    def write_hdr_mobile(out_file):
        out_file.write("""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>title</title>
    <link rel="stylesheet" href="template/github-markdown-mobile.css">

    <meta name="viewport" content="user-scalable=no, width=device-width, initial-scale=1.0" />
    <meta name="apple-mobile-web-app-capable" content="yes" />

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


    def build_toolip_help_list(self, json_data, out_file):
        next_id = 0
        self.map_url_to_id = {}
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

        out_file.write(r"""
        ];
</script>
""")

    @staticmethod
    def write_js_pc( out_file):

        out_file.write("""
<script>
function h(elem) {
    var isNumber = /^\d+$/.test(elem.title);
    if (isNumber) {
        elem.title = tool_tip_array[ elem.title ];
    }
}
</script>
""")

    @staticmethod
    def write_js_mobile(out_file):

        out_file.write("""
<script>
function h(elem) {
    elem.classList.toggle('down');
    next_element_id = parseInt(elem.id) + 1
    divelm = document.getElementById(next_element_id);
    console.log("elm " + elem.id + " " + next_element_id + " inner" + divelm. innerHTML);
    if (divelm.innerHTML == "") {
        divelm.innerHTML = tool_tip_array[ elem.title ];
    } else {
        divelm.innerHTML = "";
    }
}
</script>
""")



    def get_title(self, url):
        description = self.desc_cache.cache_get(url)
        if description is None or description.description == "":
            return url

        desc = description.description

        if desc.find('"') != -1:
            #print(f"Warning: description for {url} contains a quotation mark, desc: {desc}")
            desc = desc.replace('"', "&quot;")

        desc = desc.replace('\n', "\\n")

        desc = re.sub(self.clean_tag, '', desc)

        if desc.find(url) != -1:
            return desc

        return url + " - " + desc


    def show_cats(self, output_file_name, output_file_name_mobile):
        self.show_cats_pc(output_file_name)
        self.show_cats_mobile(output_file_name_mobile)
        self.write_text()

    def show_text(self, text):
        if self.mode == DuckStuff.MODE_SHOW_ALL_LANGUAGES:
            # check if this is not a regular expression.
            if self.check_for_regx is None:
                self.check_for_regex = re.compile(r'^(http[s]?)://.*$')
            if self.check_for_regex.match(text) is None:
                print(text)
                self.text_set[text] = 1
                self.out_file.write(text)



    def show_cats_mobile(self, output_file_name):

        all_bangs, num_entries, unique_bangs, json_data = self.get_all()

        with open(output_file_name, "w") as out_file:
            self.out_file = out_file
            DuckStuff.write_hdr_mobile(out_file)
            self.build_toolip_help_list(json_data, out_file)
            DuckStuff.write_js_mobile(out_file)

            out_file.write("<table><tr><th>")
            self.show_text("Category")
            out_file.write("</th><th>")
            self.show_text("Sub categories")
            out_file.write("</th></tr>\n")

            link_num = 1

            all_bangs_keys = list(all_bangs)
            all_bangs_keys.sort()

            for cat in all_bangs_keys:

                is_first = True

                all_bangs_cat = list(all_bangs[cat])
                all_bangs_cat.sort()

                out_file.write("<tr><td>")
                self.show_text(f"{cat}")
                out_file.write("</td><td>")

                for catentry in all_bangs_cat:
                    if not is_first:
                        out_file.write(",")

                    out_file.write("&nbsp;")
                    is_first = False
                    out_file.write(f"<a href=\"#{link_num}\">")
                    self.show_text(f"{catentry}")
                    out_file.write("</a>")

                    link_num = link_num + 1

                out_file.write("</td>\n")
            out_file.write("</table>\n")

            id_item = link_num+1
            link_num = 1

            for cat in all_bangs_keys:

                all_bangs_cat = list(all_bangs[cat])
                all_bangs_cat.sort()

                for catentry in all_bangs_cat:
                    out_file.write(f"<hr/><p/><a id=\"{link_num}\"/>\n")
                    link_num += 1

                    out_file.write("<hr>")
                    self.show_text(f"{cat}")
                    out_file.write(" / ")
                    self.show_text(f"{catentry}")
                    out_file.write("</h3><p></p>\n")

                    pos = 0
                    out_file.write("<table>\n")

                    cat_content = sorted(all_bangs[cat][catentry], key=lambda entry : entry[1])

                    for bang in cat_content:
                        out_file.write("<tr><td>")
                        out_file.write(f"<div id=\"{id_item}\" title=\"{self.map_url_to_id[bang[2]]}\" onclick=\"h(this)\" class='arrow'></div>&nbsp;<span><a href=\"javascript:onBang('{bang[0]}')\">")
                        self.show_text(f"{bang[1]}")
                        out_file.write(f"</a></span> <span style=\"float: right\">!<a href=\"javascript:onBang('{bang[0]}')\">{bang[0]}</a></span> &nbsp;")

                        id_item += 1
                        out_file.write(f"<br><div id=\"{id_item}\"></div>")
                        id_item += 1
                        out_file.write("</td>")
                        out_file.write("</tr>")
                        pos = pos + 1

                    out_file.write("</table>")

            out_file.write("\n<table width='100%'><tr><td>")
            self.show_text("Generated on ")
            out_file.write(f"{datetime.now()}; ")
            self.show_text("number of entries ")
            out_file.write(f"{num_entries} ")
            self.show_text("unique bangs")
            out_file.write(f"{unique_bangs}</td></tr></table>\n<p><p><p>***eof***\n")

    def write_text(self):
        if self.mode == DuckStuff.MODE_SHOW_ALL_LANGUAGES:
            print("writing ui string...")
            with open(globs.Globals.ui_text_strings, "w") as out_file:
                for item in self.text_set.keys():
                    out_file.write(f"{item}\n")


    def show_cats_pc(self, output_file_name):

        all_bangs, num_entries, unique_bangs, json_data = self.get_all()

        #pprint(all_bangs)

        with open(output_file_name, "w") as out_file:

            DuckStuff.write_hdr_pc(out_file)
            self.build_toolip_help_list(json_data, out_file)
            DuckStuff.write_js_pc(out_file)

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
                        out_file.write(f"<span align=\"left\"><a title=\"{self.map_url_to_id[bang[2]]}\" onmouseenter=\"h(this)\" href=\"javascript:onBang('{bang[0]}')\">{bang[1]}</a></span> <span style=\"float: right\">!<a title=\"{self.map_url_to_id[bang[2]]}\" onmouseenter=\"h(this)\" href=\"javascript:onBang('{bang[0]}')\">{bang[0]}</a></span> &nbsp;")
                        out_file.write("</td>")
                        pos = pos + 1

                    while True:
                        if pos % num_columns == 0:
                            break
                        out_file.write("<td></td>")
                        pos = pos + 1

                    out_file.write("</tr></table>")

            out_file.write(f"\n<table width='100%'><tr><td>Generated on {datetime.now()}; number of entries {num_entries} unique bangs! {unique_bangs}</td></tr></table>\n<p><p><p>***eof***\n")


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
        "--no-http-client",
        "-l",
        default=True,
        action="store_false",
        dest="http_client",
        help="disable default python http client http.client (default: enabled)"
    )

    group.add_argument(
        "--timeout",
        "-w",
        type=int,
        default=None,
        dest="timeout",
        help="timeout in seconds for https client (does not effect selenium)",
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

    duck = DuckStuff(cmd.http_client, cmd.selenium, DuckStuff.MODE_SHOW_ALL_LANGUAGES)

    if cmd.build_cache:
        print("Building descriptions...")
        duck.build_cache()

    if cmd.timeout is not None:
        scrapscrap.Global.timeout_sec = cmd.timeout

    if cmd.build_html:
        print("Building html file...")
        duck.show_cats("all_cats.html", "all_cats_mobile.html")

if __name__ == '__main__':
    _run_cmd()

#for link in BeautifulSoup(data, parse_only=SoupStrainer('a')):
#    if link.has_attr('href'):
    #        print(link['href'])
