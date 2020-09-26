import re
import http.client as client
import ssl
import json
from pprint import pprint
from datetime import datetime
#from bs4 import BeautifulSoup, SoupStrainer


class Global:
   trace_on = False

#
# get soup over tls 1.2
#
class BSoup:

    def __init__(self):
        self.map_host_to_conn = {}
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

    def get_data(self, host, path, port=443):
        conn = self.map_host_to_conn.get(host)

        if conn is None:
            conn = client.HTTPSConnection(host, context=self.context)
            self.map_host_to_conn[host] = conn

        conn.request("GET", path)

        resp = conn.getresponse()

        data = resp.read()

        if Global.trace_on:
            print("host={} path={} data={}\n".format(host, path, data))

        return data


    def get_json(self, host, path, port=443):

        data = self.get_data(host, path, port)

        json_rep = json.loads(data)

        if Global.trace_on:
            pprint(json_rep)

        return json_rep
 
    def get_soup(self, host, path, port=443):

        data = self.get_data(host, path, port)

        return BeautifulSoup(data)


class DuckStuff:
    #the host
    url='duckduckgo.com'

    def __init__(self):
        self.soup_builder = BSoup()


    def get_all(self):
        json = self.soup_builder.get_json(DuckStuff.url,"/bang.js")

        all_bangs = dict()
        for entry in json:
            #print("Category {} SubCategory {}".format(entry.get("c"), entry.get("sc")))
            sub_cat = entry.get("sc")
            cat = entry.get("c")
            if not cat is None and not sub_cat is None:
                cat_obj = all_bangs.get(cat)
                if cat_obj is None:
                    all_bangs[ cat ] = dict()
                    cat_obj = all_bangs.get(cat)

                sub_cat_obj = cat_obj.get(sub_cat)
                if sub_cat_obj is None:
                    cat_obj[ sub_cat ] = list()
                    sub_cat_obj = cat_obj.get(sub_cat)

                entry = ( entry.get("t"), entry.get("s"), entry.get("d") )
                sub_cat_obj.append( entry )


        if Global.trace_on:
            pprint(all_bangs)

        return all_bangs
        

    def get_categories(self):

        ms = self.soup_builder.get_soup(DuckStuff.url, "/bang")

        ret_cats = []

        for tag in ms.findAll('script'):
            src_path = tag.get('src')

            if not src_path is None:
                data = self.soup_builder.get_data(DuckStuff.url, src_path)
                data_str = data.decode("utf-8")

                if data_str.find("BangCategories={") != -1:
                    rex = re.search(r"BangCategories={([^}]*)}", data_str)
                    if not rex is None:
                        cts = re.findall( r"[^:]*:\[[^\]]*\],?", rex.group(1))
                        for onectg in cts:
                            tg = re.search(r"[^:]*", onectg).group(0)
                            entries = re.findall(r"\"[^\"]*\"", onectg)
                            ret_cats.append( ( tg, entries) )

        return ret_cats


    def show_cats(self, output_file_name):
        all_bangs = self.get_all()

        #pprint(all_bangs) 

        with open(output_file_name,"w") as f:

            f.write("""
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

            f.write("<table><tr><th>Category</th><th>Sub categories</th></tr>\n")
            link_num=1

            all_bangs_keys = list(all_bangs)
            all_bangs_keys.sort()

            for cat in all_bangs_keys:
                entryLinks = ""

                for catentry in list(all_bangs[cat]):
                                    entryLinks = entryLinks +  "<a href=\"#{}\">{}</a>&nbsp;".format(link_num, catentry)
                                    link_num = link_num + 1
                f.write("<tr><td>{}</td><td>{}</td>\n".format(cat, entryLinks))
            f.write("</table>\n")

            link_num = 1
            num_columns = 3

            for cat in all_bangs_keys:
                for catentry in list(all_bangs[cat]):
                    f.write("<hr/><p/><a id=\"{}\"/>\n".format(link_num))
                    link_num += 1

                    f.write("<h3>{} / {}</h3><p></p>\n".format(cat, catentry))

                    pos = 0
                    f.write("<table width=\"100%\"><tr>\n")

                    for bang in all_bangs[cat][catentry]:
                        if pos % num_columns == 0:
                            f.write("</tr><tr>")
                        f.write("<td>")
                        f.write("<span align=\"left\"><a title=\"{}\" href=\"javascript:onBang('{}')\">{}</a></span> <span style=\"float: right\">!<a title=\"{}\" href=\"javascript:onBang('{}')\">{}</a></span> &nbsp;".format(bang[2], bang[0], bang[1], bang[2], bang[0], bang[0]))
                        f.write("</td>")
                        pos = pos + 1

                    while True:
                        if pos % num_columns == 0:
                            break
                        f.write("<td></td>")
                        pos = pos + 1

                    f.write("</tr></table>")
                    
            f.write("\n<br/><br/><br/>Generated on {} <br/>\n".format(datetime.now()))

  
#---

d = DuckStuff()

d.show_cats("all_cats.html")

#for link in BeautifulSoup(data, parse_only=SoupStrainer('a')):
#    if link.has_attr('href'):
#        print(link['href'])
