#!/usr/bin/env python3

import argparse
import traceback
import sys
from comm import *

#Relevant tags to search for:
#
#<meta name="description" content="BitChute aims to put creators first and provide them with a service that they can use to flourish and express their ideas freely." />
#<meta name="twitter:title" content="BitChute is a peer-to-peer social video platform.">
#<meta name="twitter:description" content="BitChute aims to put creators first and provide them with a service that they can use to flourish and express their ideas freely.">
#<meta property="og:title" content="BitChute is a peer-to-peer social video platform." />
#<meta property="og:description" content="BitChute aims to put creators first and provide them with a service that they can use to flourish and express their ideas freely." />


def get_meta_descr_impl2(url, soup_builder):
    
    descriptions = []
    titles = []
    title_tags = []
    keywords = []

    def get_content(meta):
        for key, value in meta.attrib.items():
            if key.lower() == "content":
                return value.strip()
        return None

    def is_in_list_nocmp(name, str_list):
        lower_name = name.lower()
        for name_str in str_list:
            if name_str.lower() == lower_name:
                return True
        return False

    def check_tag(tag, name):
        if name is not None:
            if is_in_list_nocmp(name, ("description", "twitter:description", "og:description")):
                content = get_content(tag)
                if content is not None:
                    descriptions.append(content)

            elif is_in_list_nocmp(name, ("title", "twitter:title", "og:title", "og:site_name")):
                content = get_content(tag)
                if content is not None:
                    titles.append(content)

            elif is_in_list_nocmp(name, ("keywords", "twitter:keywords", "og:keywords")):
                content = get_content(tag)
                if content is not None:
                    keywords.append(content)

    soup = soup_builder.get_soup(url)

    for meta in soup.iter():
        if isinstance(meta.tag,str):
            if meta.tag.endswith("}title"):
                title_text = meta.text.strip()
                if title_text != "":
                    title_tags.append( title_text )

            if meta.tag.endswith("}meta"):
                name = meta.get("name")
                if name is not None:
                    check_tag(meta, name)

                prop = meta.get("property")
                if prop is not None:
                    check_tag(meta, prop)

    if len(titles) > 0:
        the_title = max(titles,key=len)
    else:
        the_title = ""

    descr = the_title

    if len(title_tags) != 0:
        title = max(title_tags,key=len)
        if title != "" and title != the_title:
            if descr != "":
                descr += "\n"
            descr += title
    else:
        title = ""

    if len(descriptions) > 0:
        cont = max(descriptions,key=len)
    else:
        cont = ""

    if cont != "" and cont != the_title:
        if descr != "":
            descr += "\n"
        descr += cont

    if len(keywords) > 0:
        if descr != "":
            descr += "\n"
        descr += "keywords: " + max(keywords,key=len)

    print(f"url: {url} descr: {descr}")
    return descr

def get_meta_descr_impl(url, soup_builder):

    if not url.startswith("www."):
        try:
            ret = get_meta_descr_impl2("www." + url, soup_builder)
            if ret != "":
                return ret
        except Exception as ex:
            if Global.trace_on:
                print(f"(first try) failed to resolve url: www.{url} error: {ex}")
                traceback.print_exception(*sys.exc_info())

    try:
        return get_meta_descr_impl2(url, soup_builder)
    except Exception as ex:
        if Global.trace_on:
            print(f"(second try) failed to resolve url: {url} error: {ex}")
            traceback.print_exception(*sys.exc_info())

    return ""

def get_meta_descr(url):
    soup_builder = BSoup()
    return get_meta_descr_impl(url, soup_builder)

def _parse_cmd_line():
    usage = """
Show a textual description for a requested query, see command line options for more detailed info.:
"""

    parse = argparse.ArgumentParser(
        description=usage, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    group = parse.add_argument_group("view github data on current users repositories")

    group.add_argument(
        "--url",
        "-u",
        type=str,
        dest="url",
        help="get info from meta tags of text fetched for url",
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

    if cmd.verbose:
        Global.trace_on = True

    if cmd.debug:
        Global.debug_on = True

    if cmd.url is not None:
        get_meta_descr(cmd.url)

if __name__ == '__main__':
    _run_cmd()
